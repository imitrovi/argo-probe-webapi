#!/usr/bin/env python3
import datetime
import time

import requests

API_RESULTS = '/api/v2/results'
API_STATUS = '/api/v2/status'


def get_today():
    return datetime.datetime.today()


class WebAPIReportsException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class WebAPIReports:
    def __init__(self, arguments):
        self.hostname = arguments.hostname
        self.tenant_tokens = self._get_tokens(arguments.tenant_token)
        self.type = arguments.rtype
        self.day = arguments.day
        self.timeout = arguments.timeout
        self.buffer_time = arguments.buffer_time / 1000.

    @staticmethod
    def _get_tokens(tenant_tokens):
        tokens = dict()
        try:
            for item in tenant_tokens:
                tenant, token = item[0].split(":")
                tokens.update({tenant: token})

            return tokens

        except ValueError:
            raise WebAPIReportsException(
                "Wrong token definition: token needs to be defined as "
                "<TENANT_NAME>:<TENANT_TOKEN>"
            )

    def _get_reports(self):
        reports = dict()
        for tenant, token in self.tenant_tokens.items():
            try:
                response = requests.get(
                    f"https://{self.hostname}/api/v2/reports",
                    headers={"Accept": "application/json", "x-api-key": token},
                    timeout=self.timeout
                )
                time.sleep(self.buffer_time)
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
            tenant_performance = dict()
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
                        time.sleep(self.buffer_time)

                        response.raise_for_status()

                        results = response.json()
                        response_time = response.elapsed.total_seconds()
                        response_size = len(response.content)

                        tenant_performance.update({
                            name: {
                                "time": response_time,
                                "size": response_size
                            }
                        })

                        if results:
                            try:
                                if self.type == "ar":
                                    obj = "availability"
                                    assert results["results"][0][
                                        "endpoints"
                                    ][0]["results"][0]["availability"]

                                else:
                                    assert results["groups"][0]["statuses"]

                                tenant_results.update({name: "OK"})

                            except (KeyError, AssertionError, TypeError):
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

                check_results.update({
                    tenant: {
                        "results": tenant_results,
                        "performance": tenant_performance
                    }
                })

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

    def _number_of_tenants(self):
        return len(self.data.keys())

    def _get_info(self):
        report_errors = dict()
        tenants_with_errors = list()
        time = 0
        size = 0
        for tenant, data in self.data.items():
            report_with_error = list()
            for key, value in data.items():
                if key == "REPORTS_EXCEPTION":
                    tenants_with_errors.append(tenant)
                    continue

                else:
                    if key == "results":
                        for report, status in value.items():
                            if status != "OK":
                                report_with_error.append(report)

                    else:
                        for report, perf_data in value.items():
                            if perf_data["time"] > time:
                                time = perf_data["time"]
                                size = perf_data["size"]

            if len(report_with_error) > 0:
                report_errors.update({tenant: report_with_error})

        performance_data = ""
        if time != 0 and size != 0:
            performance_data = f"|time={round(time, 6)}s;size={size}B"

        return report_errors, tenants_with_errors, performance_data

    def get_message(self):
        reports_errors, tenants_errors, perf_data = self._get_info()
        if not (reports_errors or tenants_errors):
            if self._number_of_tenants() == 1:
                first_line = (
                    f"OK - {self._capitalize_rtype()} results available for "
                    f"all reports{perf_data}"
                )

            else:
                first_line = (
                    f"OK - {self._capitalize_rtype()} results available for "
                    f"all tenants and reports{perf_data}"
                )

        else:
            first_line = "CRITICAL - Problem"

            if reports_errors:
                first_line = f"{first_line} with {self.rtype} results for"

                for tenant, reports in reports_errors.items():
                    if self._number_of_tenants() == 1:
                        first_line = (
                            f"{first_line} report(s) {', '.join(reports)}"
                        )

                    else:
                        first_line = (
                            f"{first_line} report(s) "
                            f"{', '.join(reports)} for tenant {tenant};"
                        )

            if tenants_errors:
                if first_line.endswith("Problem"):
                    if self._number_of_tenants() == 1:
                        first_line = f"{first_line} fetching all reports"
                    else:
                        first_line = (
                            f"{first_line} fetching all reports for "
                            f"tenant(s) {', '.join(tenants_errors)}"
                        )

                else:
                    first_line = (f"{first_line} problem fetching all reports "
                                  f"for tenant(s) {', '.join(tenants_errors)}")

            first_line = first_line.strip(";")
            first_line = f"{first_line}{perf_data}"

        if self.verbosity == 0:
            return first_line

        else:
            multiline = [first_line]
            for tenant, data in self.data.items():
                if self._number_of_tenants() > 1:
                    multiline.append(f"{tenant}:")

                for key, value in data.items():
                    if key == "REPORTS_EXCEPTION":
                        multiline.append(value)

                    elif key == "results":
                        for report, status in value.items():
                            multiline.append(
                                f"{self._capitalize_rtype()} for report "
                                f"{report} - {status}"
                            )

                    else:
                        continue

                multiline[-1] = f"{multiline[-1]}\n"

            return "\n".join(multiline).strip()

    def get_code(self):
        reports_errors, tenant_errors, perf_data = self._get_info()
        if reports_errors or tenant_errors:
            return self.CRITICAL

        else:
            return self.OK
