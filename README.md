# argo-probe-webapi

The package contains the probe `web-api`. This is a probe for checking AR and status reports are properly working. It checks if there are available AR and status data for a selected day.

## Synopsis

```
# /usr/libexec/argo/probes/webapi/web-api --help
usage: web-api [-h] -H HOSTNAME -k TENANT:<token> --rtype RTYPE
               [--unused-reports UNUSEDREPORTS [UNUSEDREPORTS ...]]
               [--day DAY] [-t TIMEOUT] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -H HOSTNAME           hostname
  -k                    tenant and token(authentication token) to check
  --rtype RTYPE         status or ar (default ar)
  --unused-reports UNUSEDREPORTS [UNUSEDREPORTS ...]
                        Add unused reports from API
  --day DAY             days to check (ex. 1 for yesterday, 2 for days ago)
                        default yesterday
  -t TIMEOUT
  -v                    Set verbosity level
```

Example execution of probe

```
# /usr/libexec/argo/probes/webapi/web-api -H "api.argo.grnet.gr" -t 120 --token -k TENANT:<token> --rtype ar --unused-reports REPORT3 Test --day 1
OK - All ar reports for tenant TENANT return results 
Description:OK - Availability for REPORT1 is OK
OK - Availability for REPORT2 is OK
OK - Availability for REPORT3 is OK
OK - Availability for REPORT4 is OK
```
