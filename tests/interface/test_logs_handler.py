"""
Tests for POST logs
"""
import time
from datetime import datetime

import requests

from elasticsearch import Elasticsearch

BASE_URL = "http://localhost:8000/api/1/service/1"


def test_post_log():
    """
    Checks that post logs returns 200 and
    that the log is actually inserted into ES
    """
    es_client = Elasticsearch(hosts=["elasticsearch"],)

    es_client.delete_by_query(
        index="data-*",
        body={
            "query": {
                "match_all": {}
            }
        }
    )
    time.sleep(3)

    json = {
        "logs": [
            {
                "message": "log message",
                "level": "low",
                "category": "category",
                "date": "1502304972",
            }
        ]
    }

    response = requests.post(
        BASE_URL + "/logs",
        json=json,
    )
    assert response.status_code == 200
    time.sleep(3)

    now = datetime.now()
    index = "data-1-%04d-%02d-%02d" % (
        now.year,
        now.month,
        now.day,
    )

    result = es_client.search(
        index=index,
        body={
            "query": {
                "bool": {
                    "must": {
                        "match": {
                            "service_id": "1"
                        },
                        "match": {
                            "date": datetime.fromtimestamp(1502304972.0)
                        }
                    },
                }
            }
        }
    )

    logs_amount = result["hits"]["total"]
    assert logs_amount == 1, \
        "unexpected logs amount, got %s, expected 1" % logs_amount


def test_get_logs():
    """
    Checks taht get logs returns 200 and the expected log content
    """
    es_client = Elasticsearch(hosts=["elasticsearch"],)

    es_client.delete_by_query(
        index="data-*",
        body={
            "query": {
                "match_all": {}
            }
        }
    )
    time.sleep(3)

    LOG_MESSAGE = "a message to get"
    LOG_LEVEL = "low"
    LOG_CATEGORY = "a category"

    es_client.create(
        index="data-1-2017-08-01",
        doc_type="logs",
        id="1",
        body={
            "service_id": "1",
            "message": LOG_MESSAGE,
            "level": LOG_LEVEL,
            "category": LOG_CATEGORY,
            "date": datetime.utcfromtimestamp(float("1502885498")),
        }
    )
    time.sleep(3)

    response = requests.get(
        BASE_URL + "/logs/2017-08-16-10-00-00/2017-08-16-16-00-00",
    )
    assert response.status_code == 200
    assert len(response.json()["logs"]) == 1

    log = response.json()["logs"][0]

    assert log["message"] == LOG_MESSAGE
    assert log["level"] == LOG_LEVEL
    assert log["category"] == LOG_CATEGORY
