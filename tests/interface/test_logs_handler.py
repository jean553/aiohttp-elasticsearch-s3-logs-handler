"""
Tests for POST logs
"""

import pytest
import requests
import json

BASE_URL = "http://localhost:8000/api/1/service/1"

def test_post_log():
    """
    Checks that post logs returns 200
    """
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
