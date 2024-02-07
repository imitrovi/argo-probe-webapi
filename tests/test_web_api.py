import datetime
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch, call

import requests
from argo_probe_webapi.web_api import WebAPIReports, Status

mock_reports1 = {
    "status": {
        "message": "Success",
        "code": "200"
    },
    "data": [
        {
            "id": "xxxxxxxxxx",
            "tenant": "TENANT1",
            "disabled": False,
            "info": {
                "name": "REPORT1",
                "description": "First report for testing",
                "created": "2018-09-28 15:08:48",
                "updated": "2023-06-20 14:56:11"
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
                    "id": "xxxxx",
                    "name": "ARGO_MON_1",
                    "type": "metric"
                },
                {
                    "id": "xxxx",
                    "name": "test1",
                    "type": "aggregation"
                },
                {
                    "id": "xxxxxx",
                    "name": "ops",
                    "type": "operations"
                }
            ],
            "filter_tags": [
                {
                    "name": "scope",
                    "value": "REPORT1",
                    "context": "argo.group.filter.tags.array"
                },
                {
                    "name": "production",
                    "value": "1",
                    "context": "argo.endpoint.filter.tags"
                },
                {
                    "name": "monitored",
                    "value": "1",
                    "context": "argo.endpoint.filter.tags"
                }
            ]
        },
        {
            "id": "xxxxx",
            "tenant": "TENANT1",
            "disabled": False,
            "info": {
                "name": "REPORT2",
                "description": "Test job 2",
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
                    "name": "ARGO_MON2",
                    "type": "metric"
                },
                {
                    "id": "xxxxx",
                    "name": "aggr-test",
                    "type": "aggregation"
                },
                {
                    "id": "xxxxx",
                    "name": "ops",
                    "type": "operations"
                },
                {
                    "id": "xxxxx",
                    "name": "test-thresholds",
                    "type": "thresholds"
                }
            ],
            "filter_tags": []
        },
        {
            "id": "xxxx",
            "tenant": "TENANT1",
            "disabled": True,
            "info": {
                "name": "TEST-REPORT3",
                "description": "test1",
                "created": "2022-07-11 17:06:38",
                "updated": "2023-04-11 10:37:55"
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
                "availability": 1,
                "reliability": 2,
                "uptime": 3,
                "unknown": 4,
                "downtime": 5
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
                    "name": "TEST_PROFILE",
                    "type": "metric"
                },
                {
                    "id": "xxxx",
                    "name": "test_aggregation",
                    "type": "aggregation"
                },
                {
                    "id": "xxxx",
                    "name": "ops",
                    "type": "operations"
                },
                {
                    "id": "xxxx",
                    "name": "TEST_PROFILE",
                    "type": "thresholds"
                }
            ],
            "filter_tags": []
        }
    ]
}

mock_reports2 = {
    "status": {
        "message": "Success",
        "code": "200"
    },
    "data": [
        {
            "id": "xxxxx",
            "tenant": "TENANT2",
            "disabled": False,
            "info": {
                "name": "CORE",
                "description": "Core Report",
                "created": "2021-01-28 17:01:30",
                "updated": "2022-06-29 11:30:43"
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
                "availability": 95,
                "reliability": 98,
                "uptime": 0.95,
                "unknown": 0.1,
                "downtime": 0.1
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
                    "name": "OPS",
                    "type": "metric"
                },
                {
                    "id": "xxxx",
                    "name": "ops",
                    "type": "operations"
                },
                {
                    "id": "xxxxx",
                    "name": "CORE",
                    "type": "aggregation"
                }
            ],
            "filter_tags": [
                {
                    "name": "production",
                    "value": "Y",
                    "context": ""
                },
                {
                    "name": "monitored",
                    "value": "Y",
                    "context": ""
                }
            ]
        }
    ]
}

mock_ar_results11 = {
    "results": [
        {
            "name": "TENANT1",
            "type": "PROJECT",
            "endpoints": [
                {
                    "name": "TENANT1_ENDPOINT1",
                    "type": "SERVICEGROUPS",
                    "results": [
                        {
                            "timestamp": "0001-01",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        },
                        {
                            "timestamp": "0001-01",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                },
                {
                    "name": "TENANT1_ENDPOINT2",
                    "type": "SERVICEGROUPS",
                    "results": [
                        {
                            "timestamp": "0001-01",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        },
                        {
                            "timestamp": "0001-01",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                },
                {
                    "name": "TENANT1_ENDPOINT3",
                    "type": "SERVICEGROUPS",
                    "results": [
                        {
                            "timestamp": "0001-01",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        },
                        {
                            "timestamp": "0001-01",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                }
            ]
        }
    ]
}

mock_ar_results12 = {
    "results": [
        {
            "name": "SITE1",
            "type": "NGI",
            "endpoints": [
                {
                    "name": "SITE1-PROD",
                    "type": "SITES",
                    "results": [
                        {
                            "timestamp": "2024-02-04",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                }
            ]
        },
        {
            "name": "SITE2",
            "type": "NGI",
            "endpoints": [
                {
                    "name": "TEST",
                    "type": "SITES",
                    "results": [
                        {
                            "timestamp": "2024-02-04",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                }
            ]
        }
    ]
}

mock_ar_results21 = {
    "results": [
        {
            "name": "AAI",
            "type": "NGI",
            "endpoints": [
                {
                    "name": "Fabric_Monitoring",
                    "type": "SITES",
                    "results": [
                        {
                            "timestamp": "2024-02-04",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                },
                {
                    "name": "Infrastructure_proxy",
                    "type": "SITES",
                    "results": [
                        {
                            "timestamp": "2024-02-04",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                },
                {
                    "name": "Bridge",
                    "type": "SITES",
                    "results": [
                        {
                            "timestamp": "2024-02-04",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                }
            ]
        },
        {
            "name": "Accounting",
            "type": "NGI",
            "endpoints": [
                {
                    "name": "Accounting_Services",
                    "type": "SITES",
                    "results": [
                        {
                            "timestamp": "2024-02-04",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                },
                {
                    "name": "Accounting_for_Research",
                    "type": "SITES",
                    "results": [
                        {
                            "timestamp": "2024-02-04",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                }
            ]
        }
    ]
}

mock_wrong_ar_results12 = {
    "results": [
        {
            "name": "SITE1",
            "type": "NGI",
            "endpoints": [
                {
                    "name": "SITE1-PROD",
                    "type": "SITES",
                    "results": [
                        {
                            "timestamp": "2024-02-04",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                }
            ]
        },
        {
            "name": "SITE2",
            "type": "NGI",
            "endpoints": [
                {
                    "name": "TEST",
                    "type": "SITES",
                    "results": [
                        {
                            "timestamp": "2024-02-04",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                }
            ]
        }
    ]
}

mock_empty_availability_ar_results21 = {
    "results": [
        {
            "name": "AAI",
            "type": "NGI",
            "endpoints": [
                {
                    "name": "Fabric_Monitoring",
                    "type": "SITES",
                    "results": [
                        {
                            "timestamp": "2024-02-04",
                            "availability": "",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                },
                {
                    "name": "Infrastructure_proxy",
                    "type": "SITES",
                    "results": [
                        {
                            "timestamp": "2024-02-04",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                },
                {
                    "name": "Bridge",
                    "type": "SITES",
                    "results": [
                        {
                            "timestamp": "2024-02-04",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                }
            ]
        },
        {
            "name": "Accounting",
            "type": "NGI",
            "endpoints": [
                {
                    "name": "Accounting_Services",
                    "type": "SITES",
                    "results": [
                        {
                            "timestamp": "2024-02-04",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                },
                {
                    "name": "Accounting_for_Research",
                    "type": "SITES",
                    "results": [
                        {
                            "timestamp": "2024-02-04",
                            "availability": "100",
                            "reliability": "100",
                            "unknown": "0",
                            "uptime": "1",
                            "downtime": "0"
                        }
                    ]
                }
            ]
        }
    ]
}

mock_status_results11 = {
    "groups": [
        {
            "name": "TENANT1_GROUP1",
            "type": "SERVICEGROUPS",
            "statuses": [
                {
                    "timestamp": "2024-02-04T00:00:00Z",
                    "value": "OK"
                },
                {
                    "timestamp": "2024-02-04T23:59:59Z",
                    "value": "OK"
                }
            ]
        },
        {
            "name": "TENANT1_GROUP2",
            "type": "SERVICEGROUPS",
            "statuses": [
                {
                    "timestamp": "2024-02-04T00:00:00Z",
                    "value": "OK"
                },
                {
                    "timestamp": "2024-02-04T23:59:59Z",
                    "value": "OK"
                }
            ]
        },
        {
            "name": "TENANT1_GROUP3",
            "type": "SERVICEGROUPS",
            "statuses": [
                {
                    "timestamp": "2024-02-04T00:00:00Z",
                    "value": "OK"
                },
                {
                    "timestamp": "2024-02-04T23:59:59Z",
                    "value": "OK"
                }
            ]
        }
    ]
}

mock_status_results12 = {
    "groups": [
        {
            "name": "SITE1",
            "type": "SITES",
            "statuses": [
                {
                    "timestamp": "2024-02-04T00:00:00Z",
                    "value": "CRITICAL"
                },
                {
                    "timestamp": "2024-02-04T23:59:59Z",
                    "value": "CRITICAL"
                }
            ]
        },
        {
            "name": "SITE2",
            "type": "SITES",
            "statuses": [
                {
                    "timestamp": "2024-02-04T00:00:00Z",
                    "value": "DOWNTIME"
                },
                {
                    "timestamp": "2024-02-04T23:59:59Z",
                    "value": "DOWNTIME"
                }
            ]
        }
    ]
}

mock_status_results21 = {
    "groups": [
        {
            "name": "Helpdesk",
            "type": "SITES",
            "statuses": [
                {
                    "timestamp": "2024-02-04T00:00:00Z",
                    "value": "OK"
                },
                {
                    "timestamp": "2024-02-04T23:59:59Z",
                    "value": "OK"
                }
            ]
        },
        {
            "name": "Accounting_Services",
            "type": "SITES",
            "statuses": [
                {
                    "timestamp": "2024-02-04T00:00:00Z",
                    "value": "OK"
                },
                {
                    "timestamp": "2024-02-04T23:59:59Z",
                    "value": "OK"
                }
            ]
        },
        {
            "name": "Accounting_for_Research",
            "type": "SITES",
            "statuses": [
                {
                    "timestamp": "2024-02-04T00:00:00Z",
                    "value": "OK"
                },
                {
                    "timestamp": "2024-02-04T23:59:59Z",
                    "value": "OK"
                }
            ]
        }
    ]
}

mock_wrong_status_results12 = {
    "groups": [
        {
            "name": "SITE1",
            "type": "SITES",
        },
        {
            "name": "SITE2",
            "type": "SITES",
            "statuses": [
                {
                    "timestamp": "2024-02-04T00:00:00Z",
                    "value": "DOWNTIME"
                },
                {
                    "timestamp": "2024-02-04T23:59:59Z",
                    "value": "DOWNTIME"
                }
            ]
        }
    ]
}

mock_empty_statuses_status_results21 = {
    "groups": [
        {
            "name": "Helpdesk",
            "type": "SITES",
            "statuses": []
        },
        {
            "name": "Accounting_Services",
            "type": "SITES",
            "statuses": [
                {
                    "timestamp": "2024-02-04T00:00:00Z",
                    "value": "OK"
                },
                {
                    "timestamp": "2024-02-04T23:59:59Z",
                    "value": "OK"
                }
            ]
        },
        {
            "name": "Accounting_for_Research",
            "type": "SITES",
            "statuses": [
                {
                    "timestamp": "2024-02-04T00:00:00Z",
                    "value": "OK"
                },
                {
                    "timestamp": "2024-02-04T23:59:59Z",
                    "value": "OK"
                }
            ]
        }
    ]
}


class MockResponse:
    def __init__(self, data, status_code):
        self.data = data
        self.status_code = status_code
        self.elapsed = datetime.timedelta(seconds=0.3827)
        if self.data:
            self.content = json.dumps(self.data)

        else:
            self.content = "500 BAD REQUEST"

        if self.status_code == 200:
            self.reason = "OK"

        else:
            self.reason = "SERVER ERROR"

    def json(self):
        return self.data

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.exceptions.RequestException("Error has occurred")


def mock_check_ar_result(*args, **kwargs):
    if "REPORT1" in args[0]:
        return MockResponse(
            data=mock_ar_results11,
            status_code=200
        )

    elif "REPORT2" in args[0]:
        return MockResponse(
            data=mock_ar_results12,
            status_code=200
        )

    else:
        return MockResponse(
            data=mock_ar_results21,
            status_code=200
        )


def mock_check_status_result(*args, **kwargs):
    if "REPORT1" in args[0]:
        return MockResponse(
            data=mock_status_results11,
            status_code=200
        )

    elif "REPORT2" in args[0]:
        return MockResponse(
            data=mock_status_results12,
            status_code=200
        )

    else:
        return MockResponse(
            data=mock_status_results21,
            status_code=200
        )


def mock_check_wrong_ar_result(*args, **kwargs):
    if "REPORT1" in args[0]:
        return MockResponse(
            data=mock_ar_results11,
            status_code=200
        )

    elif "REPORT2" in args[0]:
        return MockResponse(
            data=mock_wrong_ar_results12,
            status_code=200
        )

    else:
        return MockResponse(
            data=mock_ar_results21,
            status_code=200
        )


def mock_check_wrong_status_result(*args, **kwargs):
    if "REPORT1" in args[0]:
        return MockResponse(
            data=mock_status_results11,
            status_code=200
        )

    elif "REPORT2" in args[0]:
        return MockResponse(
            data=mock_wrong_status_results12,
            status_code=200
        )

    else:
        return MockResponse(
            data=mock_status_results21,
            status_code=200
        )


def mock_check_empty_availability_ar_result(*args, **kwargs):
    if "REPORT1" in args[0]:
        return MockResponse(
            data=mock_ar_results11,
            status_code=200
        )

    elif "REPORT2" in args[0]:
        return MockResponse(
            data=mock_ar_results12,
            status_code=200
        )

    else:
        return MockResponse(
            data=mock_empty_availability_ar_results21,
            status_code=200
        )


def mock_check_emtpy_statuses_status_result(*args, **kwargs):
    if "REPORT1" in args[0]:
        return MockResponse(
            data=mock_status_results11,
            status_code=200
        )

    elif "REPORT2" in args[0]:
        return MockResponse(
            data=mock_status_results12,
            status_code=200
        )

    else:
        return MockResponse(
            data=mock_empty_statuses_status_results21,
            status_code=200
        )


def mock_check_ar_result_with_response_error(*args, **kwargs):
    if "REPORT1" in args[0]:
        return MockResponse(
            data=None,
            status_code=500
        )

    elif "REPORT2" in args[0]:
        return MockResponse(
            data=mock_ar_results12,
            status_code=200
        )

    else:
        return MockResponse(
            data=mock_ar_results21,
            status_code=200
        )


def mock_check_status_result_with_response_error(*args, **kwargs):
    if "REPORT1" in args[0]:
        return MockResponse(
            data=None,
            status_code=500
        )

    elif "REPORT2" in args[0]:
        return MockResponse(
            data=mock_status_results12,
            status_code=200
        )

    else:
        return MockResponse(
            data=mock_status_results21,
            status_code=200
        )


class WebAPIReportsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.arguments = {
            "tenant_token": [
                ["TENANT1:tenant1-token"], ["TENANT2:tenant2-token"]
            ],
            "hostname": "api.devel.argo.grnet.gr",
            "timeout": 30,
            "rtype": "status",
            "day": 1,
            "debug": 0
        }

    @patch("argo_probe_webapi.web_api.requests.get")
    def test_get_reports_successfully(self, mock_get):
        mock_get.side_effect = [
            MockResponse(data=mock_reports1, status_code=200),
            MockResponse(data=mock_reports2, status_code=200)
        ]
        webapi = WebAPIReports(SimpleNamespace(**self.arguments))
        reports = webapi._get_reports()
        self.assertEqual(mock_get.call_count, 2)
        mock_get.assert_has_calls([
            call(
                "https://api.devel.argo.grnet.gr/api/v2/reports",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/reports",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant2-token"
                },
                timeout=30
            )
        ], any_order=True)
        self.assertEqual(reports, {
            "TENANT1": {
                "data": [
                    mock_reports1["data"][0],
                    mock_reports1["data"][1],
                ]
            },
            "TENANT2": {
                "data": mock_reports2["data"]
            }
        })

    @patch("argo_probe_webapi.web_api.requests.get")
    def test_get_reports_with_error_with_one_tenant(self, mock_get):
        mock_get.side_effect = [
            MockResponse(data=None, status_code=500),
            MockResponse(data=mock_reports2, status_code=200)
        ]
        webapi = WebAPIReports(SimpleNamespace(**self.arguments))
        reports = webapi._get_reports()
        self.assertEqual(mock_get.call_count, 2)
        mock_get.assert_has_calls([
            call(
                "https://api.devel.argo.grnet.gr/api/v2/reports",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/reports",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant2-token"
                },
                timeout=30
            )
        ], any_order=True)
        self.assertEqual(
            reports, {
                "TENANT1": {
                    "exception": "CRITICAL - Error fetching reports for tenant "
                                 "TENANT1: Error has occurred"
                },
                "TENANT2": {
                    "data": mock_reports2["data"]
                }
            }
        )

    @patch("argo_probe_webapi.web_api.requests.get")
    def test_get_reports_with_error_with_two_tenants(self, mock_get):
        mock_get.side_effect = [
            MockResponse(data=None, status_code=500),
            MockResponse(data=None, status_code=500)
        ]
        webapi = WebAPIReports(SimpleNamespace(**self.arguments))
        reports = webapi._get_reports()
        self.assertEqual(mock_get.call_count, 2)
        mock_get.assert_has_calls([
            call(
                "https://api.devel.argo.grnet.gr/api/v2/reports",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/reports",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant2-token"
                },
                timeout=30
            )
        ], any_order=True)
        self.assertEqual(
            reports, {
                "TENANT1": {
                    "exception": "CRITICAL - Error fetching reports for tenant "
                                 "TENANT1: Error has occurred"
                },
                "TENANT2": {
                    "exception": "CRITICAL - Error fetching reports for tenant "
                                 "TENANT2: Error has occurred"
                }
            }
        )

    @patch("argo_probe_webapi.web_api.get_today")
    @patch("argo_probe_webapi.web_api.requests.get")
    @patch("argo_probe_webapi.web_api.WebAPIReports._get_reports")
    def test_check_ar_results_all_ok(
            self, mock_get_reports, mock_get, mock_today
    ):
        mock_get_reports.return_value = {
            "TENANT1": {
                "data": [mock_reports1["data"][0], mock_reports1["data"][1]]
            },
            "TENANT2": {"data": mock_reports2["data"]}
        }
        mock_get.side_effect = mock_check_ar_result
        mock_today.return_value = datetime.datetime(2024, 2, 5, 15, 33, 24)
        arguments = self.arguments.copy()
        arguments["rtype"] = "ar"
        webapi = WebAPIReports(SimpleNamespace(**arguments))
        results = webapi.check()
        self.assertEqual(mock_get.call_count, 3)
        mock_get.assert_has_calls([
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/REPORT1/"
                "SERVICEGROUPS?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/REPORT2/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/CORE/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant2-token"
                },
                timeout=30
            )
        ])
        self.assertEqual(
            results, {
                "TENANT1": {
                    "results": {
                        "REPORT1": "OK",
                        "REPORT2": "OK"
                    },
                    "performance": {
                        "REPORT1": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_ar_results11))
                        },
                        "REPORT2": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_ar_results12))
                        }
                    }
                },
                "TENANT2": {
                    "results": {
                        "CORE": "OK"
                    },
                    "performance": {
                        "CORE": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_ar_results21))
                        }
                    }
                }
            }
        )

    @patch("argo_probe_webapi.web_api.get_today")
    @patch("argo_probe_webapi.web_api.requests.get")
    @patch("argo_probe_webapi.web_api.WebAPIReports._get_reports")
    def test_check_ar_results_with_exception_in_fetching_all_reports(
            self, mock_get_reports, mock_get, mock_today
    ):
        mock_get_reports.return_value = {
            "TENANT1": {
                "data": [mock_reports1["data"][0], mock_reports1["data"][1]]
            },
            "TENANT2": {"data": mock_reports2["data"]},
            "TENANT3": {
                "exception": "CRITICAL - Error fetching reports for tenant "
                             "TENANT1: Error has occurred"
            }
        }
        mock_get.side_effect = mock_check_ar_result
        mock_today.return_value = datetime.datetime(2024, 2, 5, 15, 33, 24)
        arguments = self.arguments.copy()
        arguments["rtype"] = "ar"
        webapi = WebAPIReports(SimpleNamespace(**arguments))
        results = webapi.check()
        self.assertEqual(mock_get.call_count, 3)
        mock_get.assert_has_calls([
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/REPORT1/"
                "SERVICEGROUPS?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/REPORT2/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/CORE/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant2-token"
                },
                timeout=30
            )
        ])
        self.assertEqual(
            results, {
                "TENANT1": {
                    "results": {
                        "REPORT1": "OK",
                        "REPORT2": "OK"
                    },
                    "performance": {
                        "REPORT1": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_ar_results11))
                        },
                        "REPORT2": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_ar_results12))
                        }
                    }
                },
                "TENANT2": {
                    "results": {
                        "CORE": "OK"
                    },
                    "performance": {
                        "CORE": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_ar_results21))
                        }
                    }
                },
                "TENANT3": {
                    "REPORTS_EXCEPTION":
                        "CRITICAL - Error fetching reports for tenant TENANT1: "
                        "Error has occurred"
                }
            }
        )

    @patch("argo_probe_webapi.web_api.get_today")
    @patch("argo_probe_webapi.web_api.requests.get")
    @patch("argo_probe_webapi.web_api.WebAPIReports._get_reports")
    def test_check_ar_results_with_error(
            self, mock_get_reports, mock_get, mock_today
    ):
        mock_get_reports.return_value = {
            "TENANT1": {
                "data": [mock_reports1["data"][0], mock_reports1["data"][1]]
            },
            "TENANT2": {"data": mock_reports2["data"]}
        }
        mock_get.side_effect = mock_check_wrong_ar_result
        mock_today.return_value = datetime.datetime(2024, 2, 5, 15, 33, 24)
        arguments = self.arguments.copy()
        arguments["rtype"] = "ar"
        webapi = WebAPIReports(SimpleNamespace(**arguments))
        results = webapi.check()
        self.assertEqual(mock_get.call_count, 3)
        mock_get.assert_has_calls([
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/REPORT1/"
                "SERVICEGROUPS?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/REPORT2/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/CORE/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant2-token"
                },
                timeout=30
            )
        ])
        self.assertEqual(
            results, {
                "TENANT1": {
                    "results": {
                        "REPORT1": "OK",
                        "REPORT2": "CRITICAL - Unable to retrieve availability "
                                   "from report REPORT2"
                    },
                    "performance": {
                        "REPORT1": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_ar_results11))
                        },
                        "REPORT2": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_wrong_ar_results12))
                        }
                    }
                },
                "TENANT2": {
                    "results": {
                        "CORE": "OK"
                    },
                    "performance": {
                        "CORE": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_ar_results21))
                        }
                    }
                }
            }
        )

    @patch("argo_probe_webapi.web_api.get_today")
    @patch("argo_probe_webapi.web_api.requests.get")
    @patch("argo_probe_webapi.web_api.WebAPIReports._get_reports")
    def test_check_ar_results_with_emtpy_availability(
            self, mock_get_reports, mock_get, mock_today
    ):
        mock_get_reports.return_value = {
            "TENANT1": {
                "data": [mock_reports1["data"][0], mock_reports1["data"][1]]
            },
            "TENANT2": {"data": mock_reports2["data"]}
        }
        mock_get.side_effect = mock_check_empty_availability_ar_result
        mock_today.return_value = datetime.datetime(2024, 2, 5, 15, 33, 24)
        arguments = self.arguments.copy()
        arguments["rtype"] = "ar"
        webapi = WebAPIReports(SimpleNamespace(**arguments))
        results = webapi.check()
        self.assertEqual(mock_get.call_count, 3)
        mock_get.assert_has_calls([
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/REPORT1/"
                "SERVICEGROUPS?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/REPORT2/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/CORE/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant2-token"
                },
                timeout=30
            )
        ])
        self.assertEqual(
            results, {
                "TENANT1": {
                    "results": {
                        "REPORT1": "OK",
                        "REPORT2": "OK"
                    },
                    "performance": {
                        "REPORT1": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_ar_results11))
                        },
                        "REPORT2": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_ar_results12))
                        }
                    }
                },
                "TENANT2": {
                    "results": {
                        "CORE": "CRITICAL - Unable to retrieve availability from "
                                "report CORE"
                    },
                    "performance": {
                        "CORE": {
                            "time": 0.3827,
                            "size": len(
                                json.dumps(mock_empty_availability_ar_results21)
                            )
                        }
                    }
                }
            }
        )

    @patch("argo_probe_webapi.web_api.get_today")
    @patch("argo_probe_webapi.web_api.requests.get")
    @patch("argo_probe_webapi.web_api.WebAPIReports._get_reports")
    def test_check_ar_results_with_response_exception(
            self, mock_get_reports, mock_get, mock_today
    ):
        mock_get_reports.return_value = {
            "TENANT1": {
                "data": [mock_reports1["data"][0], mock_reports1["data"][1]]
            },
            "TENANT2": {"data": mock_reports2["data"]}
        }
        mock_get.side_effect = mock_check_ar_result_with_response_error
        mock_today.return_value = datetime.datetime(2024, 2, 5, 15, 33, 24)
        arguments = self.arguments.copy()
        arguments["rtype"] = "ar"
        webapi = WebAPIReports(SimpleNamespace(**arguments))
        results = webapi.check()
        self.assertEqual(mock_get.call_count, 3)
        mock_get.assert_has_calls([
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/REPORT1/"
                "SERVICEGROUPS?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/REPORT2/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/results/CORE/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z&granularity=daily",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant2-token"
                },
                timeout=30
            )
        ])
        self.assertEqual(
            results, {
                "TENANT1": {
                    "results": {
                        "REPORT1": "CRITICAL - Unable to retrieve availability "
                                   "for report REPORT1: Error has occurred",
                        "REPORT2": "OK"
                    },
                    "performance": {
                        "REPORT2": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_ar_results12))
                        }
                    }
                },
                "TENANT2": {
                    "results": {
                        "CORE": "OK"
                    },
                    "performance": {
                        "CORE": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_ar_results21))
                        }
                    }
                }
            }
        )

    @patch("argo_probe_webapi.web_api.get_today")
    @patch("argo_probe_webapi.web_api.requests.get")
    @patch("argo_probe_webapi.web_api.WebAPIReports._get_reports")
    def test_check_status_results_all_ok(
            self, mock_get_reports, mock_get, mock_today
    ):
        mock_get_reports.return_value = {
            "TENANT1": {
                "data": [mock_reports1["data"][0], mock_reports1["data"][1]]
            },
            "TENANT2": {"data": mock_reports2["data"]}
        }
        mock_get.side_effect = mock_check_status_result
        mock_today.return_value = datetime.datetime(2024, 2, 5, 15, 33, 24)
        arguments = self.arguments.copy()
        arguments["rtype"] = "status"
        webapi = WebAPIReports(SimpleNamespace(**arguments))
        results = webapi.check()
        self.assertEqual(mock_get.call_count, 3)
        mock_get.assert_has_calls([
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/REPORT1/"
                "SERVICEGROUPS?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/REPORT2/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/CORE/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant2-token"
                },
                timeout=30
            )
        ])
        self.assertEqual(
            results, {
                "TENANT1": {
                    "results": {
                        "REPORT1": "OK",
                        "REPORT2": "OK"
                    },
                    "performance": {
                        "REPORT1": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_status_results11))
                        },
                        "REPORT2": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_status_results12))
                        }
                    }
                },
                "TENANT2": {
                    "results": {
                        "CORE": "OK"
                    },
                    "performance": {
                        "CORE": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_status_results21))
                        }
                    }
                }
            }
        )

    @patch("argo_probe_webapi.web_api.get_today")
    @patch("argo_probe_webapi.web_api.requests.get")
    @patch("argo_probe_webapi.web_api.WebAPIReports._get_reports")
    def test_check_status_results_with_exception_in_fetching_all_reports(
            self, mock_get_reports, mock_get, mock_today
    ):
        mock_get_reports.return_value = {
            "TENANT1": {
                "data": [mock_reports1["data"][0], mock_reports1["data"][1]]
            },
            "TENANT2": {"data": mock_reports2["data"]},
            "TENANT3": {
                "exception": "CRITICAL - Error fetching reports for tenant "
                             "TENANT1: Error has occurred"
            }
        }
        mock_get.side_effect = mock_check_status_result
        mock_today.return_value = datetime.datetime(2024, 2, 5, 15, 33, 24)
        arguments = self.arguments.copy()
        arguments["rtype"] = "status"
        webapi = WebAPIReports(SimpleNamespace(**arguments))
        results = webapi.check()
        self.assertEqual(mock_get.call_count, 3)
        mock_get.assert_has_calls([
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/REPORT1/"
                "SERVICEGROUPS?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/REPORT2/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/CORE/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant2-token"
                },
                timeout=30
            )
        ])
        self.assertEqual(
            results, {
                "TENANT1": {
                    "results": {
                        "REPORT1": "OK",
                        "REPORT2": "OK"
                    },
                    "performance": {
                        "REPORT1": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_status_results11))
                        },
                        "REPORT2": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_status_results12))
                        }
                    }
                },
                "TENANT2": {
                    "results": {
                        "CORE": "OK"
                    },
                    "performance": {
                        "CORE": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_status_results21))
                        }
                    }
                },
                "TENANT3": {
                    "REPORTS_EXCEPTION":
                        "CRITICAL - Error fetching reports for tenant TENANT1: "
                        "Error has occurred"
                }
            }
        )

    @patch("argo_probe_webapi.web_api.get_today")
    @patch("argo_probe_webapi.web_api.requests.get")
    @patch("argo_probe_webapi.web_api.WebAPIReports._get_reports")
    def test_check_status_results_with_error(
            self, mock_get_reports, mock_get, mock_today
    ):
        mock_get_reports.return_value = {
            "TENANT1": {
                "data": [mock_reports1["data"][0], mock_reports1["data"][1]]
            },
            "TENANT2": {"data": mock_reports2["data"]}
        }
        mock_get.side_effect = mock_check_wrong_status_result
        mock_today.return_value = datetime.datetime(2024, 2, 5, 15, 33, 24)
        arguments = self.arguments.copy()
        arguments["rtype"] = "status"
        webapi = WebAPIReports(SimpleNamespace(**arguments))
        results = webapi.check()
        self.assertEqual(mock_get.call_count, 3)
        mock_get.assert_has_calls([
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/REPORT1/"
                "SERVICEGROUPS?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/REPORT2/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/CORE/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant2-token"
                },
                timeout=30
            )
        ])
        self.assertEqual(
            results, {
                "TENANT1": {
                    "results": {
                        "REPORT1": "OK",
                        "REPORT2": "CRITICAL - Unable to retrieve status from "
                                   "report REPORT2"
                    },
                    "performance": {
                        "REPORT1": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_status_results11))
                        },
                        "REPORT2": {
                            "time": 0.3827,
                            "size": len(
                                json.dumps(mock_wrong_status_results12)
                            ),
                        }
                    }
                },
                "TENANT2": {
                    "results": {
                        "CORE": "OK"
                    },
                    "performance": {
                        "CORE": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_status_results21))
                        }
                    }
                }
            }
        )

    @patch("argo_probe_webapi.web_api.get_today")
    @patch("argo_probe_webapi.web_api.requests.get")
    @patch("argo_probe_webapi.web_api.WebAPIReports._get_reports")
    def test_check_status_results_with_empty_statuses(
            self, mock_get_reports, mock_get, mock_today
    ):
        mock_get_reports.return_value = {
            "TENANT1": {
                "data": [mock_reports1["data"][0], mock_reports1["data"][1]]
            },
            "TENANT2": {"data": mock_reports2["data"]}
        }
        mock_get.side_effect = mock_check_emtpy_statuses_status_result
        mock_today.return_value = datetime.datetime(2024, 2, 5, 15, 33, 24)
        arguments = self.arguments.copy()
        arguments["rtype"] = "status"
        webapi = WebAPIReports(SimpleNamespace(**arguments))
        results = webapi.check()
        self.assertEqual(mock_get.call_count, 3)
        mock_get.assert_has_calls([
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/REPORT1/"
                "SERVICEGROUPS?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/REPORT2/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/CORE/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant2-token"
                },
                timeout=30
            )
        ])
        self.assertEqual(
            results, {
                "TENANT1": {
                    "results": {
                        "REPORT1": "OK",
                        "REPORT2": "OK"
                    },
                    "performance": {
                        "REPORT1": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_status_results11))
                        },
                        "REPORT2": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_status_results12))
                        }
                    }
                },
                "TENANT2": {
                    "results": {
                        "CORE":
                            "CRITICAL - Unable to retrieve status from report CORE"
                    },
                    "performance": {
                        "CORE": {
                            "time": 0.3827,
                            "size": len(
                                json.dumps(mock_empty_statuses_status_results21)
                            )
                        }
                    }
                }
            }
        )

    @patch("argo_probe_webapi.web_api.get_today")
    @patch("argo_probe_webapi.web_api.requests.get")
    @patch("argo_probe_webapi.web_api.WebAPIReports._get_reports")
    def test_check_status_results_with_response_exception(
            self, mock_get_reports, mock_get, mock_today
    ):
        mock_get_reports.return_value = {
            "TENANT1": {
                "data": [mock_reports1["data"][0], mock_reports1["data"][1]]
            },
            "TENANT2": {"data": mock_reports2["data"]}
        }
        mock_get.side_effect = mock_check_status_result_with_response_error
        mock_today.return_value = datetime.datetime(2024, 2, 5, 15, 33, 24)
        arguments = self.arguments.copy()
        arguments["rtype"] = "status"
        webapi = WebAPIReports(SimpleNamespace(**arguments))
        results = webapi.check()
        self.assertEqual(mock_get.call_count, 3)
        mock_get.assert_has_calls([
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/REPORT1/"
                "SERVICEGROUPS?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/REPORT2/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant1-token"
                },
                timeout=30
            ),
            call(
                "https://api.devel.argo.grnet.gr/api/v2/status/CORE/"
                "SITES?start_time=2024-02-04T00:00:00Z&end_time="
                "2024-02-04T23:59:59Z",
                headers={
                    "Accept": "application/json", "x-api-key": "tenant2-token"
                },
                timeout=30
            )
        ])
        self.assertEqual(
            results, {
                "TENANT1": {
                    "results": {
                        "REPORT1": "CRITICAL - Unable to retrieve status for "
                                   "report REPORT1: Error has occurred",
                        "REPORT2": "OK"
                    },
                    "performance": {
                        "REPORT2": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_status_results12))
                        }
                    }
                },
                "TENANT2": {
                    "results": {
                        "CORE": "OK"
                    },
                    "performance": {
                        "CORE": {
                            "time": 0.3827,
                            "size": len(json.dumps(mock_status_results21))
                        }
                    }
                }
            }
        )


class StatusTests(unittest.TestCase):
    def test_ok_ar_reports(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "OK",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORT4": "OK",
                "REPORT5": "OK"
            },
            "TENANT3": {
                "REPORT6": "OK"
            }
        }
        status = Status(rtype="ar", data=results, verbosity=0)
        self.assertEqual(
            status.get_message(),
            "OK - AR results available for all tenants and reports"
        )
        self.assertEqual(status.get_code(), 0)

    def test_ok_ar_reports_verbose(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "OK",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORT4": "OK",
                "REPORT5": "OK"
            },
            "TENANT3": {
                "REPORT6": "OK"
            }
        }
        status = Status(rtype="ar", data=results, verbosity=1)
        self.assertEqual(
            status.get_message(),
            "OK - AR results available for all tenants and reports\n"
            "TENANT1:\n"
            "AR for report REPORT1 - OK\n"
            "AR for report REPORT2 - OK\n"
            "AR for report REPORT3 - OK\n\n"
            "TENANT2:\n"
            "AR for report REPORT4 - OK\n"
            "AR for report REPORT5 - OK\n\n"
            "TENANT3:\n"
            "AR for report REPORT6 - OK"
        )
        self.assertEqual(status.get_code(), 0)

    def test_error_with_ar_reports(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "CRITICAL - Unable to retrieve availability from "
                           "report REPORT2",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORT4": "OK",
                "REPORT5": "OK"
            }
        }
        status = Status(rtype="ar", data=results, verbosity=0)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem with AR results for report(s) REPORT2 for "
            "tenant TENANT1"
        )
        self.assertEqual(status.get_code(), 2)

    def test_error_fetching_all_reports_for_ar_reports(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "CRITICAL - Unable to retrieve availability for "
                           "report REPORT2",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORTS_EXCEPTION": "CRITICAL - Error fetching reports"
            },
            "TENANT3": {
                "REPORT4": "OK",
                "REPORT5": "OK"
            }
        }
        status = Status(rtype="ar", data=results, verbosity=0)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem with AR results for report(s) REPORT2 for "
            "tenant TENANT1; problem fetching all reports for tenant(s) TENANT2"
        )
        self.assertEqual(status.get_code(), 2)

    def test_error_fetching_all_reports_for_ar_reports_verbose(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "CRITICAL - Unable to retrieve availability for "
                           "report REPORT2",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORTS_EXCEPTION": "CRITICAL - Error fetching reports"
            },
            "TENANT3": {
                "REPORT4": "OK",
                "REPORT5": "OK"
            }
        }
        status = Status(rtype="ar", data=results, verbosity=1)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem with AR results for report(s) REPORT2 for "
            "tenant TENANT1; problem fetching all reports for tenant(s) "
            "TENANT2\n"
            "TENANT1:\n"
            "AR for report REPORT1 - OK\n"
            "AR for report REPORT2 - CRITICAL - Unable to retrieve "
            "availability for report REPORT2\n"
            "AR for report REPORT3 - OK\n\n"
            "TENANT2:\n"
            "CRITICAL - Error fetching reports\n\n"
            "TENANT3:\n"
            "AR for report REPORT4 - OK\n"
            "AR for report REPORT5 - OK"
        )
        self.assertEqual(status.get_code(), 2)

    def test_multiple_errors_fetching_all_reports_for_ar_reports(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "OK",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORTS_EXCEPTION": "CRITICAL - Error fetching reports"
            },
            "TENANT3": {
                "REPORTS_EXCEPTION": "CRITICAL - Error fetching reports for "
                                     "tenant TENANT3: 401 Unauthorized"
            }
        }
        status = Status(rtype="ar", data=results, verbosity=0)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem fetching all reports for tenant(s) TENANT2, "
            "TENANT3"
        )
        self.assertEqual(status.get_code(), 2)

    def test_multiple_errors_fetching_all_reports_for_ar_reports_verbose(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "OK",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORTS_EXCEPTION": "CRITICAL - Error fetching reports"
            },
            "TENANT3": {
                "REPORTS_EXCEPTION": "CRITICAL - Error fetching reports for "
                                     "tenant TENANT3: 401 Unauthorized"
            }
        }
        status = Status(rtype="ar", data=results, verbosity=1)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem fetching all reports for tenant(s) "
            "TENANT2, TENANT3\n"
            "TENANT1:\n"
            "AR for report REPORT1 - OK\n"
            "AR for report REPORT2 - OK\n"
            "AR for report REPORT3 - OK\n\n"
            "TENANT2:\n"
            "CRITICAL - Error fetching reports\n\n"
            "TENANT3:\n"
            "CRITICAL - Error fetching reports for tenant TENANT3: 401 "
            "Unauthorized"
        )
        self.assertEqual(status.get_code(), 2)

    def test_error_with_ar_reports_verbose(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "CRITICAL - Unable to retrieve availability for "
                           "report REPORT2",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORT4": "OK",
                "REPORT5": "OK"
            }
        }
        status = Status(rtype="ar", data=results, verbosity=1)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem with AR results for report(s) REPORT2 for "
            "tenant TENANT1\n"
            "TENANT1:\n"
            "AR for report REPORT1 - OK\n"
            "AR for report REPORT2 - CRITICAL - Unable to retrieve "
            "availability for report REPORT2\n"
            "AR for report REPORT3 - OK\n\n"
            "TENANT2:\n"
            "AR for report REPORT4 - OK\n"
            "AR for report REPORT5 - OK"
        )
        self.assertEqual(status.get_code(), 2)

    def test_multitple_errors_with_ar_reports(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "CRITICAL - Unable to retrieve availability from "
                           "report REPORT2",
                "REPORT3": "CRITICAL - BAD REQUEST"
            },
            "TENANT2": {
                "REPORT4": "CRITICAL - Unable to retrieve availability",
                "REPORT5": "OK"
            }
        }
        status = Status(rtype="ar", data=results, verbosity=0)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem with AR results for report(s) REPORT2, REPORT3 "
            "for tenant TENANT1; report(s) REPORT4 for tenant TENANT2"
        )
        self.assertEqual(status.get_code(), 2)

    def test_multiple_errors_with_ar_reports_verbose(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "CRITICAL - Unable to retrieve availability for "
                           "report REPORT2",
                "REPORT3": "CRITICAL - BAD REQUEST"
            },
            "TENANT2": {
                "REPORT4": "CRITICAL - Unable to retrieve availability",
                "REPORT5": "OK"
            }
        }
        status = Status(rtype="ar", data=results, verbosity=1)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem with AR results for report(s) REPORT2, REPORT3 "
            "for tenant TENANT1; report(s) REPORT4 for tenant TENANT2\n"
            "TENANT1:\n"
            "AR for report REPORT1 - OK\n"
            "AR for report REPORT2 - CRITICAL - Unable to retrieve "
            "availability for report REPORT2\n"
            "AR for report REPORT3 - CRITICAL - BAD REQUEST\n\n"
            "TENANT2:\n"
            "AR for report REPORT4 - CRITICAL - Unable to retrieve "
            "availability\n"
            "AR for report REPORT5 - OK"
        )
        self.assertEqual(status.get_code(), 2)

    def test_ok_status_reports(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "OK",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORT4": "OK",
                "REPORT5": "OK"
            },
            "TENANT3": {
                "REPORT6": "OK"
            }
        }
        status = Status(rtype="status", data=results, verbosity=0)
        self.assertEqual(
            status.get_message(),
            "OK - Status results available for all tenants and reports"
        )
        self.assertEqual(status.get_code(), 0)

    def test_ok_status_reports_verbose(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "OK",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORT4": "OK",
                "REPORT5": "OK"
            },
            "TENANT3": {
                "REPORT6": "OK"
            }
        }
        status = Status(rtype="status", data=results, verbosity=1)
        self.assertEqual(
            status.get_message(),
            "OK - Status results available for all tenants and reports\n"
            "TENANT1:\n"
            "Status for report REPORT1 - OK\n"
            "Status for report REPORT2 - OK\n"
            "Status for report REPORT3 - OK\n\n"
            "TENANT2:\n"
            "Status for report REPORT4 - OK\n"
            "Status for report REPORT5 - OK\n\n"
            "TENANT3:\n"
            "Status for report REPORT6 - OK"
        )
        self.assertEqual(status.get_code(), 0)

    def test_error_fetching_all_reports_for_status_reports(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "CRITICAL - Unable to retrieve status for report "
                           "REPORT2",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORTS_EXCEPTION": "CRITICAL - Error fetching reports"
            },
            "TENANT3": {
                "REPORT6": "OK"
            }
        }
        status = Status(rtype="status", data=results, verbosity=0)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem with status results for report(s) REPORT2 for "
            "tenant TENANT1; problem fetching all reports for tenant(s) TENANT2"
        )
        self.assertEqual(status.get_code(), 2)

    def test_error_fetching_all_reports_for_status_reports_verbose(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "CRITICAL - Unable to retrieve status for report "
                           "REPORT2",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORTS_EXCEPTION": "CRITICAL - Error fetching reports"
            },
            "TENANT3": {
                "REPORT6": "OK"
            }
        }
        status = Status(rtype="status", data=results, verbosity=1)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem with status results for report(s) REPORT2 for "
            "tenant TENANT1; problem fetching all reports for tenant(s) "
            "TENANT2\n"
            "TENANT1:\n"
            "Status for report REPORT1 - OK\n"
            "Status for report REPORT2 - CRITICAL - Unable to retrieve status "
            "for report REPORT2\n"
            "Status for report REPORT3 - OK\n\n"
            "TENANT2:\n"
            "CRITICAL - Error fetching reports\n\n"
            "TENANT3:\n"
            "Status for report REPORT6 - OK"
        )
        self.assertEqual(status.get_code(), 2)

    def test_multiple_errors_fetching_all_reports_for_status_reports(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "OK",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORTS_EXCEPTION": "CRITICAL - Error fetching reports"
            },
            "TENANT3": {
                "REPORTS_EXCEPTION": "CRITICAL - Error fetching reports for "
                                     "tenant TENANT3: 401 Unauthorized"
            }
        }
        status = Status(rtype="status", data=results, verbosity=0)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem fetching all reports for tenant(s) TENANT2, "
            "TENANT3"
        )
        self.assertEqual(status.get_code(), 2)

    def test_multiple_errors_fetching_all_reports_for_status_reports_verbose(
            self
    ):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "OK",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORTS_EXCEPTION": "CRITICAL - Error fetching reports"
            },
            "TENANT3": {
                "REPORTS_EXCEPTION": "CRITICAL - Error fetching reports for "
                                     "tenant TENANT3: 401 Unauthorized"
            }
        }
        status = Status(rtype="status", data=results, verbosity=1)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem fetching all reports for tenant(s) "
            "TENANT2, TENANT3\n"
            "TENANT1:\n"
            "Status for report REPORT1 - OK\n"
            "Status for report REPORT2 - OK\n"
            "Status for report REPORT3 - OK\n\n"
            "TENANT2:\n"
            "CRITICAL - Error fetching reports\n\n"
            "TENANT3:\n"
            "CRITICAL - Error fetching reports for tenant TENANT3: 401 "
            "Unauthorized"
        )
        self.assertEqual(status.get_code(), 2)

    def test_error_with_status_reports(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "CRITICAL - Unable to retrieve status for report "
                           "REPORT2",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORT4": "OK",
                "REPORT5": "OK"
            }
        }
        status = Status(rtype="status", data=results, verbosity=0)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem with status results for report(s) REPORT2 for "
            "tenant TENANT1"
        )
        self.assertEqual(status.get_code(), 2)

    def test_error_with_status_reports_verbose(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "CRITICAL - Unable to retrieve status for report "
                           "REPORT2",
                "REPORT3": "OK"
            },
            "TENANT2": {
                "REPORT4": "OK",
                "REPORT5": "OK"
            }
        }
        status = Status(rtype="status", data=results, verbosity=1)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem with status results for report(s) REPORT2 for "
            "tenant TENANT1\n"
            "TENANT1:\n"
            "Status for report REPORT1 - OK\n"
            "Status for report REPORT2 - CRITICAL - Unable to retrieve status "
            "for report REPORT2\n"
            "Status for report REPORT3 - OK\n\n"
            "TENANT2:\n"
            "Status for report REPORT4 - OK\n"
            "Status for report REPORT5 - OK"
        )
        self.assertEqual(status.get_code(), 2)

    def test_multitple_errors_with_status_reports(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "CRITICAL - Unable to retrieve status for "
                           "report REPORT2",
                "REPORT3": "CRITICAL - BAD REQUEST"
            },
            "TENANT2": {
                "REPORT4": "CRITICAL - Unable to retrieve status",
                "REPORT5": "OK"
            }
        }
        status = Status(rtype="status", data=results, verbosity=0)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem with status results for report(s) REPORT2, "
            "REPORT3 for tenant TENANT1; report(s) REPORT4 for tenant TENANT2"
        )
        self.assertEqual(status.get_code(), 2)

    def test_multiple_errors_with_status_reports_verbose(self):
        results = {
            "TENANT1": {
                "REPORT1": "OK",
                "REPORT2": "CRITICAL - Unable to retrieve status for "
                           "report REPORT2",
                "REPORT3": "CRITICAL - BAD REQUEST"
            },
            "TENANT2": {
                "REPORT4": "CRITICAL - Unable to retrieve status",
                "REPORT5": "OK"
            }
        }
        status = Status(rtype="status", data=results, verbosity=1)
        self.assertEqual(
            status.get_message(),
            "CRITICAL - Problem with status results for report(s) REPORT2, "
            "REPORT3 for tenant TENANT1; report(s) REPORT4 for tenant TENANT2\n"
            "TENANT1:\n"
            "Status for report REPORT1 - OK\n"
            "Status for report REPORT2 - CRITICAL - Unable to retrieve status "
            "for report REPORT2\n"
            "Status for report REPORT3 - CRITICAL - BAD REQUEST\n\n"
            "TENANT2:\n"
            "Status for report REPORT4 - CRITICAL - Unable to retrieve status\n"
            "Status for report REPORT5 - OK"
        )
        self.assertEqual(status.get_code(), 2)
