#!/usr/bin/env python3
import requests
import argparse
import datetime
from datetime import timedelta

API_REPORTS = '/api/v2/reports'
API_RESULTS = '/api/v2/results'
API_STATUS = '/api/v2/status'


def createAPICallUrl(arguments):
    """Create the main API Call Reports Url to get the
       profile and the topology.
       Args:
           arguments: the main input arguments.
    """
    profilesjson_list = list()
    for i in range(len(arguments.tenant_token)):
        token = arguments.tenant_token[i][0].split(":")[1]

        try:
            # create the main headers for json call
            headers = {'Accept': 'application/json', 'x-api-key': token}

            # make the call to get the json
            profiles = requests.get('https://' + arguments.hostname +
                                    API_REPORTS, headers=headers, timeout=arguments.timeout)

            profiles.raise_for_status()
            profilesjson = profiles.json()

        # check for connection request
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
            print('CRITICAL - API cannot connect to https://' +
                  arguments.hostname + API_REPORTS)

            raise SystemExit(2)

        # Remove disabled reports from response's data results
        profilesjson["data"] = [
            x for x in profilesjson["data"] if x["disabled"] == False]
        profilesjson_list.append(profilesjson)

    return profilesjson_list


def convert_date(year, month, day, daytype):
    """Construct the correct day
       2017-05-16T00:00:00
       Args:
           year: the year
           month: the month
           day: the day
           daytype: construct the start or end date for the api call
    """
    orig_date = str(datetime.datetime(year, month, day))
    d = datetime.datetime.strptime(orig_date, '%Y-%m-%d %H:%M:%S')

    if (daytype == 'start'):
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
    ProbeDescription = list()
    for i in range(len(arguments.tenant_token)):
        token = arguments.tenant_token[i][0].split(":")[1]

        allReports = len(profilesjson[i]['data'])
        count = 0
        pathToUse = API_STATUS
        if arguments.rtype == 'ar':
            pathToUse = API_RESULTS

        a = datetime.datetime.today()
        timeBackCheck = arguments.day
        yesterday = a - timedelta(timeBackCheck)
        start = convert_date(yesterday.year, yesterday.month,
                             yesterday.day, 'start')
        end = convert_date(yesterday.year, yesterday.month,
                           yesterday.day, 'end')

        # get all report names
        descriptions_list = list()
        while (count < allReports):
            reportName = profilesjson[i]['data'][count]['info']['name']
            reportTopologyGroup = profilesjson[i]['data'][count]['topology_schema']['group']['group']['type']

            # create the main headers for json call
            try:
                headers = {'Accept': 'application/json', 'x-api-key': token}

                # make the call to get the json
                if arguments.rtype == 'ar':
                    urlToAPI = 'https://' + arguments.hostname + pathToUse+'/' + reportName+'/' + \
                        reportTopologyGroup+'?start_time='+start+'&end_time='+end+'&granularity=daily'
                else:
                    urlToAPI = 'https://' + arguments.hostname + pathToUse+'/' + reportName + \
                        '/'+reportTopologyGroup+'?start_time='+start+'&end_time=' + end

                resultsAPI = requests.get(
                    urlToAPI, headers=headers, timeout=arguments.timeout)

                count += 1
                resultsjson = resultsAPI.json()

                # raise an HTTPError exception for non 200 status codes
                if resultsAPI.status_code != 200:
                    resultsAPI.raise_for_status()

            # check for connection request
            except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
                description_report = 'CRITICAL - Reports cannot connect to (https://' + \
                    arguments.hostname + pathToUse+'/' + reportName+'/'+reportTopologyGroup+')'
                descriptions_list.append(description_report)
                description_status = 'CRITICAL - Status code error. Cannot connect to (https://' + \
                    arguments.hostname + pathToUse+'/' + reportName+'/'+reportTopologyGroup+')'
                descriptions_list.append(description_status)

            # when we have results report check the json for the string we need
            if (arguments.rtype == 'ar'):
                description = 'OK - Availability for ' + reportName + ' is OK'
                try:
                    resultsjson['results'][0]['endpoints'][0]['results'][0]['availability']
                except KeyError:
                    description = 'CRITICAL - cannot retrieve availability from ' + reportName

                descriptions_list.append(description)

            # check status report
            if (arguments.rtype == 'status'):
                description = 'OK - status for ' + reportName + ' is OK'
                try:
                    resultsjson['groups'][0]['statuses']
                except:
                    description = 'CRITICAL - cannot retrieve status from ' + reportName
                descriptions_list.append(description)

        ProbeDescription.append(descriptions_list)
        
    return ProbeDescription


def utils(arguments, output_dict):
    NAGIOS_RESULT = 0
    msgs_ok = f'Ok - {(arguments.rtype).upper()} reports for all tenant/-s return results'
    msgs_not_ok = ""

    for i in range(len(arguments.tenant_token)):
        tenant = arguments.tenant_token[i][0].split(":")[0]

        Description = ""
        if arguments.rtype not in ('status', 'ar'):
            msgs_not_ok += "CRITICAL: wrong value at argument rtype. rtype must be ar or status" \
                if "CRITICAL: wrong value at argument rtype. rtype must be ar or status" not in msgs_not_ok else ""
            msg = "CRITICAL: wrong value at argument rtype. rtype must be ar or status"
            if NAGIOS_RESULT < 2:
                NAGIOS_RESULT = 2
        else:
            for item in output_dict[i]:

                if "CRITICAL" in item:
                    msgs_not_ok += f'CRITICAL - Problem with {arguments.rtype} reports for tenant {tenant} return results' + \
                        " / " if f'CRITICAL - Problem with {arguments.rtype} reports for tenant {tenant} return results' not in msgs_not_ok else ""
                    msg = f'CRITICAL - Problem with {arguments.rtype} reports for tenant {tenant} return results'
                    if NAGIOS_RESULT < 2:
                        NAGIOS_RESULT = 2
                elif "WARNING" in item:
                    msgs_not_ok += f'WARNING - Problem with {arguments.rtype} reports for tenant {tenant} return results' + \
                        " / " if f'WARNING - Problem with {arguments.rtype} reports for tenant {tenant} return results' not in msgs_not_ok else ""
                    msg = f'WARNING - Problem with {arguments.rtype} reports for tenant {tenant} return results'
                    if NAGIOS_RESULT < 1:
                        NAGIOS_RESULT = 1
                else:
                    msg = f'Ok - All {arguments.rtype} reports for tenant {tenant} return results'
                    if NAGIOS_RESULT <= 0:
                        NAGIOS_RESULT = 0

                Description += item + "\n"

        if arguments.debug > 0:
            print(msg)
            print(f"Description: {Description}")

    print(msgs_ok if msgs_not_ok == "" else msgs_not_ok.rstrip(" / "))
    raise SystemExit(NAGIOS_RESULT)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', dest='hostname',
                        required=True, type=str, help='hostname')
    parser.add_argument('-k', dest='tenant_token',
                        required=True, type=str, nargs="+", help='tenant_token', action='append')
    parser.add_argument('--rtype', dest='rtype', required=True,
                        type=str, default='ar', help='status or ar (default ar)')
    parser.add_argument('--day', dest='day', required=False, type=int, default=1,
                        help='days to check (ex. 1 for yesterday, 2 for days ago) default yesterday')
    parser.add_argument('-t', dest='timeout',
                        required=False, type=int, default=180)
    parser.add_argument('-v', '--verbose', dest="debug",
                        help='Set verbosity level', action='count', default=0)
    arguments = parser.parse_args()

    profilejson = createAPICallUrl(arguments)
    data = CheckResults(arguments, profilejson)
    utils(arguments, data)


if __name__ == "__main__":
    main()
