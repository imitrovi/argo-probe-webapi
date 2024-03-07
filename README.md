# argo-probe-webapi

The package contains the `web-api` probe. This is a probe for checking AR and status results are available in Web-API for a given day.

## Synopsis

The probe has four required arguments: 

* hostname;
* tenant token(s) - token(s) for tenant(s); it must be defined in the form `<TENANT_NAME>:<TENANT_TOKEN>`, because the probe is designed to be multi-tenant aware;
* type of results to fetch - possible values are `ar` and `status`;
* timeout - the time in seconds after which the probe will stop execution.

There are also two optional arguments. One is `--day`, which is used to set for which period you wish to check the result. By default, the probe checks the results for previous day (`--day` parameter set to 1). You can, if you wish, check the results from, e.g., two days ago, in which case you will want to set `--day` parameter to 2.

There is also option to increase verbosity, so the probe output will show response detail per tenant and per report. 

```
# /usr/libexec/argo/probes/webapi/web-api -h
usage: web-api -H HOSTNAME -k TENANT_TOKEN [TENANT_TOKEN ...] --rtype
               {status,ar} -t TIMEOUT [--day DAY] [-v] [-h]

ARGO probe that checks ARGO Web-API for AR or status results

required arguments:
  -H HOSTNAME           hostname
  -k TENANT_TOKEN [TENANT_TOKEN ...]
                        token for authentication of tenant; must be of form
                        TENANT:token
  --rtype {status,ar}   type of results to fetch: can be status or ar (default
                        ar)
  -t TIMEOUT            seconds before connection times out (default: 180)

optional arguments:
  --day DAY             days for which to check the results; eg. 1 for one day
                        ago, 2 for two days ago (default 1)
  -v, --verbose         verbosity level; if used, the output has detailed
                        lines for individual reports
  -h, --help            Show this help message and exit
```

Example execution of probe for one tenant:

```
# /usr/libexec/argo/probes/webapi/web-api -H api.devel.argo.grnet.gr -t 120 --rtype status --day 1 -k TENANT:<TENANT_TOKEN>
OK - Status results available for all reports|time=0.279122s;size=8927B
```

Example execution of probe for one tenant with increased verbosity:

```
# /usr/libexec/argo/probes/webapi/web-api -H api.devel.argo.grnet.gr -t 120 --rtype status --day 1 -k TENANT:<TENANT_TOKEN> -v
OK - Status results available for all reports|time=0.279122s;size=8927B
Status for report REPORT1 - OK
Status for report REPORT2 - OK
Status for report REPORT3 - OK
```

Example execution of probe for multiple tenants:

```
# /usr/libexec/argo/probes/webapi/web-api -H api.devel.argo.grnet.gr -t 120 --rtype status --day 1 -k TENANT1:<TENANT1_TOKEN> -k TENANT2:<TENANT2_TOKEN>
OK - Status results available for all tenants and reports|time=0.196456s;size=5038B
```

Example execution of probe for multiple tenants with increased verbosity:

```
# /usr/libexec/argo/probes/webapi/web-api -H api.devel.argo.grnet.gr -t 120 --rtype status --day 1 -k TENANT1:<TENANT1_TOKEN> -k TENANT2:<TENANT2_TOKEN> -v
OK - Status results available for all tenants and reports|time=0.205328s;size=12637B
TENANT1:
Status for report REPORT1 - OK
Status for report REPORT2 - OK
Status for report REPORT3 - OK
TENANT2:
Status for report CORE - OK
```

