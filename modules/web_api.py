#!/usr/bin/env python3
import datetime

import requests

API_REPORTS = '/api/v2/reports'
API_RESULTS = '/api/v2/results'
API_STATUS = '/api/v2/status'


def get_today():
    return datetime.datetime.today()


class WebAPIReports:
    def __init__(self, arguments):
        self.hostname = arguments.hostname
        self.tenant_tokens = self._get_tokens(arguments.tenant_token)
        self.type = arguments.rtype
        self.day = arguments.day
        self.timeout = arguments.timeout

    @staticmethod
    def _get_tokens(tenant_tokens):
        tokens = dict()
        for item in tenant_tokens:
            tenant, token = item[0].split(":")
            tokens.update({tenant: token})

        return tokens

    def _get_reports(self):
        reports = dict()
        for tenant, token in self.tenant_tokens.items():
            try:
                response = requests.get(
                    f"https://{self.hostname}{API_REPORTS}",
                    headers={"Accept": "application/json", "x-api-key": token},
                    timeout=self.timeout
                )
                response.raise_for_status()

                reports.update({tenant: {
                    "data": [
                        report for report in response.json()["data"] if
                        report["disabled"] is False
                    ]
                }})

            except (
                requests.exceptions.RequestException,
                requests.exceptions.HTTPError
            ) as e:
                reports.update({
                    tenant: {
                        "exception": f"CRITICAL - Error fetching reports for "
                                     f"tenant {tenant}: {str(e)}"
                    }
                })

        return reports

    def check(self):
        reports = self._get_reports()

        check_results = dict()
        for tenant, tenants_reports in reports.items():
            tenant_results = dict()
            if self.type == "ar":
                path = API_RESULTS

            else:
                path = API_STATUS

            date_considered = get_today() - datetime.timedelta(days=self.day)

            if "data" in tenants_reports.keys():
                for report in tenants_reports["data"]:
                    name = report["info"]["name"]
                    url = (
                        f"https://{self.hostname}{path}/{name}/"
                        f"{report['topology_schema']['group']['group']['type']}"
                        f"?start_time="
                        f"{date_considered.strftime('%Y-%m-%dT00:00:00Z')}&"
                        f"end_time="
                        f"{date_considered.strftime('%Y-%m-%dT23:59:59Z')}"
                    )
                    if self.type == "ar":
                        url = f"{url}&granularity=daily"
                        obj = "availability"

                    else:
                        obj = "status"

                    try:
                        response = requests.get(
                            url,
                            headers={
                                "Accept": "application/json",
                                "x-api-key": self.tenant_tokens[tenant]
                            },
                            timeout=self.timeout
                        )

                        response.raise_for_status()

                        results = response.json()

                        if results:
                            try:
                                if self.type == "ar":
                                    obj = "availability"
                                    assert results["results"][0][
                                        "endpoints"
                                    ][0]["results"][0]["availability"]

                                else:
                                    assert results["groups"][0]["statuses"]

                                tenant_results.update({
                                    report["info"]["name"]: "OK"
                                })

                            except (KeyError, AssertionError):
                                tenant_results.update({
                                    name:
                                        f"CRITICAL - Unable to retrieve {obj} "
                                        f"from report {name}"
                                })

                    except (
                            requests.exceptions.RequestException,
                            requests.exceptions.HTTPError
                    ) as e:
                        tenant_results.update({
                            name: f"CRITICAL - Unable to retrieve {obj} for "
                                  f"report {name}: {str(e)}"
                        })

                check_results.update({tenant: tenant_results})

            if "exception" in tenants_reports.keys():
                check_results.update({
                    tenant: {
                        "REPORTS_EXCEPTION": tenants_reports["exception"]
                    }
                })

        return check_results


class Status:
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3

    def __init__(self, rtype, data, verbosity):
        if rtype == "ar":
            rtype = "AR"
        self.rtype = rtype
        self.data = data
        self.verbosity = verbosity

    def _capitalize_rtype(self):
        if self.rtype != "AR":
            return self.rtype.capitalize()

        else:
            return self.rtype

    def _get_errors(self):
        errors = dict()
        for tenant, reports in self.data.items():
            report_with_error = list()
            for report, status in reports.items():
                if status != "OK":
                    report_with_error.append(report)

                if len(report_with_error) > 0:
                    errors.update({tenant: report_with_error})

        return errors

    def get_message(self):
        if not self._get_errors():
            first_line = (f"OK - {self._capitalize_rtype()} results "
                          f"available for all tenants and reports")

        else:
            first_line = \
                f"CRITICAL - Problem with {self.rtype} results for"

            for tenant, reports in self._get_errors().items():
                first_line = (f"{first_line} report(s) "
                              f"{', '.join(reports)} for tenant {tenant};")

            first_line = first_line.strip(";")

        if self.verbosity == 0:
            return first_line

        else:
            multiline = [first_line]
            for tenant, reports in self.data.items():
                multiline.append(f"{tenant}:")
                for report, status in reports.items():
                    multiline.append(
                        f"{self._capitalize_rtype()} for report {report} "
                        f"- {status}"
                    )
                multiline[-1] = f"{multiline[-1]}\n"

            return "\n".join(multiline).strip()

    def get_code(self):
        if self._get_errors():
            return self.CRITICAL

        else:
            return self.OK
