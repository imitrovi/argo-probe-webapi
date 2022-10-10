#!/usr/bin/env python3
import requests
import argparse
import datetime
from datetime import timedelta

API_REPORTS = '/api/v2/reports'
API_RESULTS = '/api/v2/results'
API_STATUS = '/api/v2/status'

strerr = ''
num_excp_expand = 0
server_expire = None
NAGIOS_RESULT = 0
   

def createAPICallUrl(arguments):
    """Create the main API Call Reports Url to get the
       profile and the topology.
       Args:
           arguments: the main input arguments.
    """

    try:
        #create the main headers for json call
        headers = {'Accept': 'application/json', 'x-api-key': arguments.token}

        #make the call to get the json
        profiles = requests.get('https://' + arguments.hostname + API_REPORTS, headers = headers,timeout=arguments.timeout)
        
        profiles.raise_for_status()
        profilesjson = profiles.json()


    #check for connection request
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
        print ('CRITICAL - API cannot connect to https://' + arguments.hostname + API_REPORTS)

        raise SystemExit(2)

    # Remove disabled reports from response's data results
    profilesjson["data"] = [ x for x in profilesjson["data"] if x["disabled"] == False ]
     
    return profilesjson




def convert_date(year,month,day,daytype):
    """Construct the correct day
       2017-05-16T00:00:00
       Args:
           year: the year
           month: the month
           day: the day
           daytype: construct the start or end date for the api call
    """
    orig_date = str(datetime.datetime(year,month,day))
    d = datetime.datetime.strptime(orig_date, '%Y-%m-%d %H:%M:%S')

    if (daytype=='start'):
        d = d.strftime('%Y-%m-%dT00:00:00Z')
    else:
        d = d.strftime('%Y-%m-%dT23:59:59Z')

    return d


def CheckResults(arguments, profilesjson):
    """Create the correct call based on report profile and topology.
       Iterate to profiles and check results
       Args:
           arguments: the main input arguments
           profilesjson: the json for a tenant with the reports
    """

    allReports = len(profilesjson['data']);
    count=0
    pathToUse = API_STATUS
    if arguments.rtype == 'ar':
       pathToUse = API_RESULTS

    a = datetime.datetime.today()
    
    timeBackCheck = arguments.day
    yesterday = a - timedelta(timeBackCheck)
    
    start = convert_date(yesterday.year, yesterday.month, yesterday.day, 'start')
    end = convert_date(yesterday.year, yesterday.month, yesterday.day, 'end')
    ProbeDescription = {}
    
    debug = ""

    #get all report names
    while (count < allReports):
        reportName = profilesjson['data'][count]['info']['name']
        reportTopologyGroup = profilesjson['data'][count]['topology_schema']['group']['group']['type']

        #create the main headers for json call
        try:
            headers = {'Accept': 'application/json', 'x-api-key': arguments.token}
            #make the call to get the json
            if arguments.rtype == 'ar':
                urlToAPI = 'https://' + arguments.hostname + pathToUse+'/' +reportName+'/'+reportTopologyGroup+'?start_time='+start+'&end_time='+end+'&granularity=daily'
            else:
                urlToAPI = 'https://' + arguments.hostname + pathToUse+'/' +reportName+'/'+reportTopologyGroup+'?start_time='+start+'&end_time='+end
            resultsAPI = requests.get(urlToAPI, headers = headers, timeout=arguments.timeout)
            
            count+=1;
            if arguments.debug:
                debug = debug +  "[CheckResults] API call:"+ urlToAPI
            resultsjson = resultsAPI.json()
            
            #raise an HTTPError exception for non 200 status codes
            if resultsAPI.status_code != 200:
                resultsAPI.raise_for_status()
        #check for connection request
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
            ProbeDescription['Connection'+reportName] = 'CRITICAL - Reports cannot connect to (https://' + arguments.hostname + pathToUse+'/' +reportName+'/'+reportTopologyGroup+')'
            ProbeDescription['Status'+reportName] = 'CRITICAL - Status code error. Cannot connect to (https://' + arguments.hostname + pathToUse+'/' +reportName+'/'+reportTopologyGroup+')'


        #when we have results report
        #check the json for the string we need
        if (arguments.rtype=='ar'):
            ProbeDescription[reportName] = 'OK - Availability for ' +reportName +' is OK'
            try:
                resultsjson['results'][0]['endpoints'][0]['results'][0]['availability']
            except KeyError:
                ProbeDescription[reportName] = 'CRITICAL - cannot retrieve availability from ' +reportName

        #check status report
        if (arguments.rtype=='status'):
            ProbeDescription[reportName] = 'OK - status for ' +reportName +' is OK'
            try:
                resultsjson['groups'][0]['statuses']
            except:
                ProbeDescription[reportName] = 'CRITICAL - cannot retrieve status from ' +reportName

    return ProbeDescription, debug


def debugValues(arguments):
    """ Print debug values.
        Args:
            arguments: the input arguments
    """
    if arguments.debug:
        print ("[debugValues] - hostname:"+ arguments.hostname)
        print ("[debugValues] - tenant:" + arguments.tenant)
        print ("[debugValues] - rtype:" + arguments.rtype)
        print ("[debugValues] - token:" + arguments.token)
        if arguments.timeout!='':
            print ("[debugValues] - timeout:" + str(arguments.timeout))


def utils(arguments, output_dict):
    Description = ''
    if arguments.rtype not in ('status', 'ar'):
        NAGIOS_RESULT = 2
        msg = "CRITICAL: wrong value at argument rtype. rtype must be ar or status"
    
    else:   
        for item in output_dict:
            if "WARNING" in output_dict[item]: 
                msg = "SystemExit(1)"
                NAGIOS_RESULT = 1
            elif "CRITICAL" in output_dict[item]:
                msg = f'CRITICAL - Problem with {arguments.rtype} reports for tenant {arguments.tenant} return results'
                NAGIOS_RESULT = 2
            else:
                NAGIOS_RESULT = 0
                msg = f'Ok - All {arguments.rtype} reports for tenant {arguments.tenant} return results'
            Description += output_dict[item] + "\n"

    print(msg)
    print(f"Description: {Description}")
    
    raise SystemExit(NAGIOS_RESULT)
   

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', dest='hostname', required=True, type=str, help='hostname')
    parser.add_argument('--tenant', dest='tenant', required=True, type=str, default='EGI', help='tenant to check. Default EGI')
    parser.add_argument('--rtype', dest='rtype', required=True, type=str, default='ar', help='status or ar (default ar)')
    parser.add_argument('--token', dest='token', required=True, type=str, default='test_token', help='authentication token')
    parser.add_argument('--unused-reports', dest='unusedreports', required=False, type=str, nargs='+', help='Add unused reports from API')
    parser.add_argument('--day', dest='day', required=False, type=int, default=1, help='days to check (ex. 1 for yesterday, 2 for days ago) default yesterday')
    parser.add_argument('-t', dest='timeout', required=False, type=int, default=180)
    parser.add_argument('-v', dest='debug', help='Set verbosity level', action='count', default=0)
    arguments = parser.parse_args()

    profilejson = createAPICallUrl(arguments)
    data, debugData = CheckResults(arguments, profilejson)

    utils(arguments, output_dict=data)



if __name__ == "__main__":
    main()
