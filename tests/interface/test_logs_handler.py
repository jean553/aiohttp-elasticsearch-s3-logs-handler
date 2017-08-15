"""
Tests for POST logs
"""
import time
from datetime import datetime

import pytest
import requests

from elasticsearch import Elasticsearch, helpers

BASE_URL = "http://localhost:8000/api/1/service/1"

def test_post_log():
    """
    Checks that post logs returns 200
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

    result = es_client.search(
        index="data-1-2017-08-15",
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
