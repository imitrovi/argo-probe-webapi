import unittest
import requests
from freezegun import freeze_time
from unittest.mock import patch, call
from types import SimpleNamespace

from argo_probe_webapi.web_api import convert_date, createAPICallUrl, CheckResults, utils

mock_reports = [
    {
        "id": "xxxxxx",
        "tenant": "TENANT",
        "disabled": False,
        "info": {
            "name": "REPORT1",
            "description": "Test A/R report",
            "created": "2018-09-28 15:08:48",
            "updated": "2021-07-26 18:39:34"
        },
        "computations": {
            "ar": True,
            "status": True,
            "trends": [
                "flapping",
                "status",
                "tags"
            ]
        },
        "thresholds": {
            "availability": 80,
            "reliability": 85,
            "uptime": 0.8,
            "unknown": 0.1,
            "downtime": 0.1
        },
        "topology_schema": {
            "group": {
                "type": "PROJECT",
                "group": {
                        "type": "SERVICEGROUPS"
                }
            }
        },
        "profiles": [
            {
                "id": "xxxxxx",
                "name": "ARGO_MON_CRITICAL",
                "type": "metric"
            },
            {
                "id": "xxxx",
                "name": "sla_test",
                "type": "aggregation"
            },
            {
                "id": "xxxx",
                "name": "ops",
                "type": "operations"
            }
        ],
        "filter_tags": [
            {
                "name": "production",
                "value": "1",
                "context": "argo.endpoint.filter.tags"
            },
            {
                "name": "monitored",
                "value": "1",
                "context": "argo.endpoint.filter.tags"
            },
            {
                "name": "scope",
                "value": "SLA",
                "context": "argo.group.filter.tags.array"
            }
        ]
    },
    {
        "id": "xxxxxx",
        "tenant": "TENANT",
        "disabled": True,
        "info": {
            "name": "Test-Thresholds",
            "description": "A test job with thresholds. ",
            "created": "2021-11-04 15:45:15",
            "updated": "2022-01-31 12:10:16"
        },
        "computations": {
            "ar": True,
            "status": True,
            "trends": [
                "flapping",
                "status",
                "tags"
            ]
        },
        "thresholds": {
            "availability": 81,
            "reliability": 81,
            "uptime": 0,
            "unknown": 0,
            "downtime": 0
        },
        "topology_schema": {
            "group": {
                "type": "NGI",
                "group": {
                        "type": "SITES"
                }
            }
        },
        "profiles": [
            {
                "id": "xxxxx",
                "name": "Test-Thresholds",
                "type": "metric"
            },
            {
                "id": "xxxx",
                "name": "Test-Thresholds",
                "type": "aggregation"
            },
            {
                "id": "xxxx",
                "name": "ops",
                "type": "operations"
            },
            {
                "id": "xxxx",
                "name": "test-thresholds",
                "type": "thresholds"
            }
        ],
        "filter_tags": []
    }
]


class MockResponse:
    def __init__(self, data, status_code):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.exceptions.RequestException("Error has occured")


def mock_web_api(*args, **kwargs):
    return MockResponse(
        data={
            "status": {
                "message": "Success",
                "code": 200,
            },
            "data": mock_reports
        },
        status_code=200
    )


def mock_fail_web_api(*args, **kwargs):
    return MockResponse(
        data={
            "status": {
                "message": "Failed",
                "code": 403,
            },
            "data": mock_reports,
        },
        status_code=403
    )


mock_reports_check_results = [
    {
        'status': {
            'message': 'Success',
            'code': '200'
        },
        'data': [
            {
                'id': 'xxxxxx',
                'tenant': 'TENANT1111',
                'disabled': False,
                'info': {
                    'name': 'REPORT1111',
                    'description': 'Report for SLA service groups',
                    'created': '2019-01-25 13:51:40',
                    'updated': '2022-02-10 14:27:51'
                },
                'computations': {
                    'ar': True,
                    'status': True,
                    'trends': [
                        'flapping',
                        'status',
                        'tags'
                    ]
                },
                'thresholds': {
                    'availability': 80,
                    'reliability': 85,
                    'uptime': 0.8,
                    'unknown': 0.1,
                    'downtime': 0.1
                },
                'topology_schema': {
                    'group': {
                        'type': 'PROJECT',
                        'group': {
                            'type': 'SERVICEGROUPS1111'
                        }
                    }
                },
                'profiles': [
                    {
                        'id': 'xxxxx',
                        'name': 'ARGO_MON_CRITICAL',
                        'type': 'metric'
                    },
                    {
                        'id': 'xxxxx',
                        'name': 'sla_test',
                        'type': 'aggregation'
                    },
                    {
                        'id': 'xxxxx',
                        'name': 'ops',
                        'type': 'operations'
                    }
                ],
                'filter_tags': [
                    {
                        'name': 'production',
                        'value': '1',
                        'context': 'argo.endpoint.filter.tags'
                    },
                    {
                        'name': 'monitored',
                        'value': '1',
                        'context': 'argo.endpoint.filter.tags'
                    },
                    {
                        'name': 'scope',
                        'value': 'SLA',
                        'context': 'argo.group.filter.tags.array'
                    }
                ]
            },
            {
                'id': 'xxxxx',
                'tenant': 'TENANT2222',
                'disabled': False,
                'info': {
                    'name': 'REPORT2222',
                    'description': 'Report containing all endpoints',
                    'created': '2022-07-27 10:03:12',
                    'updated': '2022-07-27 10:03:12'
                },
                'computations': {
                    'ar': True,
                    'status': True,
                    'trends': [
                        'flapping',
                        'status',
                        'tags'
                    ]
                },
                'thresholds': {
                    'availability': 80,
                    'reliability': 85,
                    'uptime': 0.8,
                    'unknown': 0.1,
                    'downtime': 0.1
                },
                'topology_schema': {
                    'group': {
                        'type': 'NGI',
                        'group': {
                            'type': 'SERVICEGROUPS2222'
                        }
                    }
                },
                'profiles': [
                    {
                        'id': 'xxxxxxxx',
                        'name': 'ARGO_MON',
                        'type': 'metric'
                    },
                    {
                        'id': 'xxxxxxxx',
                        'name': 'argo-mon-full',
                        'type': 'aggregation'
                    },
                    {
                        'id': 'xxxxxxxxxx',
                        'name': 'egi_ops',
                        'type': 'operations'
                    }
                ],
                'filter_tags': [
                    {
                        'name': 'certification',
                        'value': 'Certified',
                        'context': 'argo.group.filter.tags.array'
                    },
                    {
                        'name': 'infrastructure',
                        'value': 'Production',
                        'context': 'argo.group.filter.tags.array'
                    },
                    {
                        'name': 'scope',
                        'value': 'EGI',
                        'context': 'argo.group.filter.tags.array'
                    },
                    {
                        'name': 'monitored',
                        'value': '1',
                        'context': 'argo.endpoint.filter.tags'
                    },
                    {
                        'name': 'scope',
                        'value': 'EGI',
                        'context': 'argo.endpoint.filter.tags.array'
                    }
                ]
            },
            {
                'id': 'xxxxxxxxxx',
                'tenant': 'TENANT3333',
                'disabled': False,
                'info': {
                    'name': 'REPORT3333',
                    'description': 'EGI Critical Report',
                    'created': '2018-03-09 14:57:02',
                    'updated': '2022-02-10 14:32:31'
                },
                'computations': {
                    'ar': True,
                    'status': True,
                    'trends': [
                        'flapping',
                        'status',
                        'tags'
                    ]
                },
                'thresholds': {
                    'availability': 80,
                    'reliability': 85,
                    'uptime': 0.8,
                    'unknown': 0.1,
                    'downtime': 0.1
                },
                'topology_schema': {
                    'group': {
                        'type': 'NGI',
                        'group': {
                            'type': 'SERVICEGROUPS3333'
                        }
                    }
                },
                'profiles': [
                    {
                        'id': 'xxxxxxxxxx',
                        'name': 'ARGO_MON_CRITICAL',
                        'type': 'metric'
                    },
                    {
                        'id': 'xxxxxxxxxxxxxxxx',
                        'name': 'egi_ops',
                        'type': 'operations'
                    },
                    {
                        'id': 'xxxxxxxxxxxx',
                        'name': 'critical',
                        'type': 'aggregation'
                    }
                ],
                'filter_tags': [
                    {
                        'name': 'certification',
                        'value': 'Certified',
                        'context': 'argo.group.filter.tags.array'
                    },
                    {
                        'name': 'infrastructure',
                        'value': 'Production',
                        'context': 'argo.group.filter.tags.array'
                    },
                    {
                        'name': 'scope',
                        'value': 'EGI',
                        'context': 'argo.group.filter.tags.array'
                    },
                    {
                        'name': 'production',
                        'value': '1',
                        'context': 'argo.endpoint.filter.tags'
                    },
                    {
                        'name': 'monitored',
                        'value': '1',
                        'context': 'argo.endpoint.filter.tags'
                    },
                    {
                        'name': 'scope',
                        'value': 'EGI',
                        'context': 'argo.endpoint.filter.tags.array'
                    }
                ]
            },
            {
                'id': 'xxxxxxxxxxxxxxxxxxx',
                'tenant': 'TENANT4444',
                'disabled': False,
                'info': {
                    'name': 'REPORT4444',
                    'description': 'EGI Report for Uncertified Sites',
                    'created': '2019-03-07 15:32:17',
                    'updated': '2022-02-10 14:37:48'
                },
                'computations': {
                    'ar': True,
                    'status': True,
                    'trends': [
                        'flapping',
                        'status',
                        'tags'
                    ]
                },
                'thresholds': {
                    'availability': 80,
                    'reliability': 85,
                    'uptime': 0.8,
                    'unknown': 0.1,
                    'downtime': 0.1
                },
                'topology_schema': {
                    'group': {
                        'type': 'NGI',
                        'group': {
                            'type': 'SERVICEGROUPS4444'
                        }
                    }
                },
                'profiles': [
                    {
                        'id': 'XXXXXXXXXXX',
                        'name': 'ARGO_MON_CRITICAL',
                        'type': 'metric'
                    },
                    {
                        'id': 'XXXXXXXXXXXXXXX',
                        'name': 'egi_ops',
                        'type': 'operations'
                    },
                    {
                        'id': 'XXXXXXXXXXXXXX',
                        'name': 'critical',
                        'type': 'aggregation'
                    }
                ],
                'filter_tags': [
                    {
                        'name': 'certification',
                        'value': 'Uncertified',
                        'context': 'argo.group.filter.tags'
                    },
                    {
                        'name': 'scope',
                        'value': 'EGI',
                        'context': 'argo.group.filter.tags.array'
                    },
                    {
                        'name': 'production',
                        'value': '1',
                        'context': 'argo.endpoint.filter.tags'
                    },
                    {
                        'name': 'monitored',
                        'value': '1',
                        'context': 'argo.endpoint.filter.tags'
                    },
                    {
                        'name': 'scope',
                        'value': 'EGI',
                        'context': 'argo.endpoint.filter.tags.array'
                    }
                ]
            },
            {
                'id': 'XXXXXXXXXXXXXXX',
                'tenant': 'TENANT5555',
                'disabled': False,
                'info': {
                    'name': 'REPORT5555',
                    'description': 'EGI report for Ops Monitoring Critical',
                    'created': '2018-03-09 15:28:02',
                    'updated': '2022-02-10 15:02:35'
                },
                'computations': {
                    'ar': True,
                    'status': True,
                    'trends': [
                        'flapping',
                        'status',
                        'tags'
                    ]
                },
                'thresholds': {
                    'availability': 80,
                    'reliability': 85,
                    'uptime': 0.8,
                    'unknown': 0.1,
                    'downtime': 0.1
                },
                'topology_schema': {
                    'group': {
                        'type': 'NGI',
                        'group': {
                            'type': 'SERVICEGROUPS5555'
                        }
                    }
                },
                'profiles': [
                    {
                        'id': 'XXXXXXXXXXXXXXXXXXXXXXXXXX',
                        'name': 'OPS_MONITOR_CRITICAL',
                        'type': 'metric'
                    },
                    {
                        'id': 'XXXXXXXXXXXXXXXXXXXXX',
                        'name': 'egi_ops',
                        'type': 'operations'
                    },
                    {
                        'id': 'XXXXXXXXXXXXXXX',
                        'name': 'ops-mon-critical',
                        'type': 'aggregation'
                    }
                ],
                'filter_tags': [
                    {
                        'name': 'certification',
                        'value': 'Certified',
                        'context': 'argo.group.filter.tags.array'
                    },
                    {
                        'name': 'infrastructure',
                        'value': 'Production',
                        'context': 'argo.group.filter.tags.array'
                    },
                    {
                        'name': 'scope',
                        'value': 'EGICore',
                        'context': 'argo.group.filter.tags.array'
                    },
                    {
                        'name': 'monitored',
                        'value': '1',
                        'context': 'argo.endpoint.filter.tags'
                    },
                    {
                        'name': 'production',
                        'value': '1',
                        'context': 'argo.endpoint.filter.tags'
                    }
                ]
            }
        ]
    }
]

mock_check_ar_results = {
    'results': [
        {
            'name': 'REPORT1111',
            'type': 'SERVICEGROUPS1111',
            'endpoints': [
                {
                    'name': 'REPORT1111',
                    'type': 'SERVICEGROUPS1111',
                    'results': [
                        {
                            'timestamp': '2022-10-03',
                            'availability': '100',
                            'reliability': '100',
                            'unknown': '0',
                            'uptime': '1',
                            'downtime': '0'
                        }
                    ]
                }
            ]
        }
    ]
}

mock_check_status_results = {
    'groups': [
        {
            'name': 'REPORT1111',
            'type': 'SERVICEGROUPS1111',
            'statuses': [
                {
                    'timestamp': '1999-09-30T00:00:00Z',
                    'value': 'OK'
                },
                {
                    'timestamp': '1999-09-30T23:59:59Z',
                    'value': 'OK'
                }
            ]
        },
    ]
}

mock_fail_check_and_ar_results = {
    "results": [
        {
            "name": "string",
            "type": "string",
            "results": [
                {
                    "timestamp": "string",
                    "availability": "string",
                    "reliability": "string"
                }
            ]
        }
    ]
}


def mock_check_ar_result(*args, **kwargs):
    return MockResponse(
        data=mock_check_ar_results,
        status_code=200
    )


def mock_fail_check_ar_and_status_result(*args, **kwargs):
    return MockResponse(
        data=mock_fail_check_and_ar_results,
        status_code=403
    )


def mock_check_status_result(*args, **kwargs):
    return MockResponse(
        data=mock_check_status_results,
        status_code=200
    )


# TODO: NE ZABORAVI POGLEDATI ISPRAVLJENO OD DANIJELA ZA WEBAPI
# TODO: POCISTI GLAVNI WEBAPI KOD

@freeze_time("1999-10-1")
class ArgoProbeWebApiTests(unittest.TestCase):
    def setUp(self) -> None:
        arguments = {"tenant_token": [["mock_tenant:1234"]], "hostname": "mock_hostname",
                     "timeout": 5, "rtype": 'status', "day": 1, "debug": 0}

        self.arguments = SimpleNamespace(**arguments)

    @patch("argo_probe_webapi.web_api.requests.get")
    def test_pass_api_call_url_ar(self, mock_request):
        mock_request.side_effect = mock_web_api

        apiCallUrl = createAPICallUrl(self.arguments)

        mock_request.assert_called_once_with("https://mock_hostname/api/v2/reports", headers={
                                             'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5)

        self.assertEqual(apiCallUrl, [{
            "status": {
                "message": "Success",
                "code": 200,
            },
            "data": [mock_reports[0]]
        }])

    @patch("builtins.print")
    @patch("argo_probe_webapi.web_api.requests.get")
    def test_fail_api_call_url(self, mock_request, mock_print):
        mock_request.side_effect = mock_fail_web_api

        with self.assertRaises(SystemExit):
            createAPICallUrl(self.arguments)

        mock_print.assert_has_calls(
            [(call("CRITICAL - API cannot connect to https://mock_hostname/api/v2/reports"))])

    def test_pass_convert_date_start(self):
        expected = convert_date(2020, 4, 22, "start")
        actual = "2020-04-22T00:00:00Z"
        self.assertEqual(expected, actual)

    def test_pass_convert_date_end(self):
        expected = convert_date(2020, 4, 22, "end")
        actual = "2020-04-22T23:59:59Z"
        self.assertEqual(expected, actual)

    def test_fail_month_conver_date(self):
        self.assertRaises(ValueError, convert_date, 2021, 14, 21, "end")

    def test_fail_day_conver_date(self):
        self.assertRaises(ValueError, convert_date, 2021, 11, 41, "start")

    @patch("argo_probe_webapi.web_api.requests.get")
    def test_check_ar_results(self, mock_request):
        mock_request.side_effect = mock_check_ar_result

        self.arguments.rtype = "ar"
        expected = CheckResults(self.arguments, mock_reports_check_results)

        calls = [
            call('https://mock_hostname/api/v2/results/REPORT1111/SERVICEGROUPS1111?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z&granularity=daily',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/results/REPORT2222/SERVICEGROUPS2222?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z&granularity=daily',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/results/REPORT3333/SERVICEGROUPS3333?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z&granularity=daily',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/results/REPORT4444/SERVICEGROUPS4444?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z&granularity=daily',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/results/REPORT5555/SERVICEGROUPS5555?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z&granularity=daily',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5)
        ]

        mock_request.assert_has_calls(calls, any_order=True)

        actual = ([[
            'OK - Availability for REPORT1111 is OK',
            'OK - Availability for REPORT2222 is OK',
            'OK - Availability for REPORT3333 is OK',
            'OK - Availability for REPORT4444 is OK',
            'OK - Availability for REPORT5555 is OK'
        ]])

        self.assertEqual(expected, actual)

    @patch("argo_probe_webapi.web_api.requests.get")
    def test_fail_check_ar_results(self, mock_request):
        mock_request.side_effect = mock_fail_check_ar_and_status_result

        self.arguments.rtype = "ar"
        expected = CheckResults(self.arguments, mock_reports_check_results)

        calls = [
            call('https://mock_hostname/api/v2/results/REPORT1111/SERVICEGROUPS1111?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z&granularity=daily',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/results/REPORT2222/SERVICEGROUPS2222?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z&granularity=daily',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/results/REPORT3333/SERVICEGROUPS3333?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z&granularity=daily',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/results/REPORT4444/SERVICEGROUPS4444?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z&granularity=daily',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/results/REPORT5555/SERVICEGROUPS5555?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z&granularity=daily',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5)
        ]

        mock_request.assert_has_calls(calls, any_order=True)

        actual = [[
            'CRITICAL - Reports cannot connect to (https://mock_hostname/api/v2/results/REPORT1111/SERVICEGROUPS1111)',
            'CRITICAL - Status code error. Cannot connect to (https://mock_hostname/api/v2/results/REPORT1111/SERVICEGROUPS1111)',
            'CRITICAL - cannot retrieve availability from REPORT1111',
            'CRITICAL - Reports cannot connect to (https://mock_hostname/api/v2/results/REPORT2222/SERVICEGROUPS2222)',
            'CRITICAL - Status code error. Cannot connect to (https://mock_hostname/api/v2/results/REPORT2222/SERVICEGROUPS2222)',
            'CRITICAL - cannot retrieve availability from REPORT2222',
            'CRITICAL - Reports cannot connect to (https://mock_hostname/api/v2/results/REPORT3333/SERVICEGROUPS3333)',
            'CRITICAL - Status code error. Cannot connect to (https://mock_hostname/api/v2/results/REPORT3333/SERVICEGROUPS3333)',
            'CRITICAL - cannot retrieve availability from REPORT3333',
            'CRITICAL - Reports cannot connect to (https://mock_hostname/api/v2/results/REPORT4444/SERVICEGROUPS4444)',
            'CRITICAL - Status code error. Cannot connect to (https://mock_hostname/api/v2/results/REPORT4444/SERVICEGROUPS4444)',
            'CRITICAL - cannot retrieve availability from REPORT4444',
            'CRITICAL - Reports cannot connect to (https://mock_hostname/api/v2/results/REPORT5555/SERVICEGROUPS5555)',
            'CRITICAL - Status code error. Cannot connect to (https://mock_hostname/api/v2/results/REPORT5555/SERVICEGROUPS5555)',
            'CRITICAL - cannot retrieve availability from REPORT5555'
        ]]

        self.assertEqual(expected, actual)

    @patch("argo_probe_webapi.web_api.requests.get")
    def test_check_status_results(self, mock_request):
        mock_request.side_effect = mock_check_status_result

        self.arguments.rtype = "status"
        expected = CheckResults(self.arguments, mock_reports_check_results)

        calls = [
            call('https://mock_hostname/api/v2/status/REPORT1111/SERVICEGROUPS1111?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/status/REPORT2222/SERVICEGROUPS2222?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/status/REPORT3333/SERVICEGROUPS3333?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/status/REPORT4444/SERVICEGROUPS4444?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/status/REPORT5555/SERVICEGROUPS5555?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5)
        ]

        mock_request.assert_has_calls(calls, any_order=True)

        actual = [[
            'OK - status for REPORT1111 is OK',
            'OK - status for REPORT2222 is OK',
            'OK - status for REPORT3333 is OK',
            'OK - status for REPORT4444 is OK',
            'OK - status for REPORT5555 is OK'
        ]]

        self.assertEqual(expected, actual)

    @patch("argo_probe_webapi.web_api.requests.get")
    def test_fail_check_status_results(self, mock_request):
        mock_request.side_effect = mock_fail_check_ar_and_status_result

        self.arguments.rtype = "status"
        expected = CheckResults(self.arguments, mock_reports_check_results)

        calls = [
            call('https://mock_hostname/api/v2/status/REPORT1111/SERVICEGROUPS1111?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/status/REPORT2222/SERVICEGROUPS2222?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/status/REPORT3333/SERVICEGROUPS3333?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/status/REPORT4444/SERVICEGROUPS4444?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5),
            call('https://mock_hostname/api/v2/status/REPORT5555/SERVICEGROUPS5555?start_time=1999-09-30T00:00:00Z&end_time=1999-09-30T23:59:59Z',
                 headers={'Accept': 'application/json', 'x-api-key': '1234'}, timeout=5)
        ]

        mock_request.assert_has_calls(calls, any_order=True)

        actual = [[
            'CRITICAL - Reports cannot connect to (https://mock_hostname/api/v2/status/REPORT1111/SERVICEGROUPS1111)',
            'CRITICAL - Status code error. Cannot connect to (https://mock_hostname/api/v2/status/REPORT1111/SERVICEGROUPS1111)',
            'CRITICAL - cannot retrieve status from REPORT1111',
            'CRITICAL - Reports cannot connect to (https://mock_hostname/api/v2/status/REPORT2222/SERVICEGROUPS2222)',
            'CRITICAL - Status code error. Cannot connect to (https://mock_hostname/api/v2/status/REPORT2222/SERVICEGROUPS2222)',
            'CRITICAL - cannot retrieve status from REPORT2222',
            'CRITICAL - Reports cannot connect to (https://mock_hostname/api/v2/status/REPORT3333/SERVICEGROUPS3333)',
            'CRITICAL - Status code error. Cannot connect to (https://mock_hostname/api/v2/status/REPORT3333/SERVICEGROUPS3333)',
            'CRITICAL - cannot retrieve status from REPORT3333',
            'CRITICAL - Reports cannot connect to (https://mock_hostname/api/v2/status/REPORT4444/SERVICEGROUPS4444)',
            'CRITICAL - Status code error. Cannot connect to (https://mock_hostname/api/v2/status/REPORT4444/SERVICEGROUPS4444)',
            'CRITICAL - cannot retrieve status from REPORT4444',
            'CRITICAL - Reports cannot connect to (https://mock_hostname/api/v2/status/REPORT5555/SERVICEGROUPS5555)',
            'CRITICAL - Status code error. Cannot connect to (https://mock_hostname/api/v2/status/REPORT5555/SERVICEGROUPS5555)',
            'CRITICAL - cannot retrieve status from REPORT5555']]

        self.assertEqual(expected, actual)

    @patch("builtins.print")
    def test_utils_fail(self, mock_print):
        self.arguments.rtype = "statussSsS"

        with self.assertRaises(SystemExit) as e:
            utils(self.arguments, {
                'SLA': 'OK - Availability for SLA is OK',
                'ALL': 'OK - Availability for ALL is OK',
                'Critical': 'OK - Availability for Critical is OK',
                'CriticalUncert': 'OK - Availability for CriticalUncert is OK',
                'OPS-MONITOR-Critical': 'OK - Availability for OPS-MONITOR-Critical is OK'})

        calls = [
            call("CRITICAL: wrong value at argument rtype. rtype must be ar or status"),
        ]

        mock_print.assert_has_calls(calls)
        self.assertEqual(e.exception.code, 2)

    @patch("builtins.print")
    def test_utils_systemexit_with_0(self, mock_print):

        with self.assertRaises(SystemExit) as e:
            utils(self.arguments, [[
                'OK - Availability for SLA is OK',
                'OK - Availability for ALL is OK',
                'OK - Availability for Critical is OK',
                'OK - Availability for CriticalUncert is OK',
                'OK - Availability for OPS-MONITOR-Critical is OK'
            ]])

        calls = [
            call('Ok - STATUS reports for all tenant/-s return results')
        ]

        mock_print.assert_has_calls(calls)
        self.assertEqual(e.exception.code, 0)

    @patch('builtins.print')
    def test_utils_systemexit_with_1(self, mock_print):
        tenant = self.arguments.tenant_token[0][0].split(":")[0]
        with self.assertRaises(SystemExit) as e:
            utils(self.arguments, [[
                'WARNING - Availability for SLA is OK',
                'WARNING - Availability for ALL is OK',
                'WARNING - Availability for Critical is OK',
                'WARNING - Availability for CriticalUncert is OK',
                'WARNING - Availability for OPS-MONITOR-Critical is OK'
            ]])
        calls = [
            call(
                f'WARNING - Problem with {self.arguments.rtype} reports for tenant {tenant} return results')
        ]

        mock_print.assert_has_calls(calls)
        self.assertEqual(e.exception.code, 1)

    @patch('builtins.print')
    def test_utils_systemexit_with_2(self, mock_print):
        tenant = self.arguments.tenant_token[0][0].split(":")[0]
        fail_report = "Critical"
        with self.assertRaises(SystemExit) as e:
            utils(self.arguments, [[
                'CRITICAL - cannot retrieve status from Critical'
            ]])

        calls = [
            call(
                f'CRITICAL - Problem with {self.arguments.rtype} report {fail_report} for tenant {tenant}'),
        ]

        mock_print.assert_has_calls(calls)
        self.assertEqual(e.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
