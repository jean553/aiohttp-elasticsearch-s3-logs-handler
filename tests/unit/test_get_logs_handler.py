import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request

from logs.get_logs_handler import get_logs


@pytest.fixture
def es_client_mock():
    return MagicMock()


@pytest.fixture
def s3_client_mock():
    return MagicMock()


@pytest.mark.asyncio
async def test_get_logs_elasticsearch_only(es_client_mock):
    # Mock Elasticsearch response
    es_response = {
        '_scroll_id': 'mock_scroll_id',
        'hits': {
            'hits': [
                {
                    '_source': {
                        'message': 'Test log 1',
                        'level': 'INFO',
                        'category': 'test',
                        'date': '2023-05-01T12:00:00'
                    }
                }
            ]
        }
    }
    
    with patch('logs.get_logs_handler._get_logs_from_elasticsearch', return_value=es_response), \
         patch('logs.get_logs_handler._scroll_logs_from_elasticsearch', return_value={'hits': {'hits': []}}):
        
        request = make_mocked_request('GET', '/logs/1/2023-05-01-00-00-00/2023-05-01-23-59-59')
        response = await get_logs(request, es_client_mock)
        
        assert isinstance(response, web.StreamResponse)
        content = await response.text()
        logs = json.loads(content)['logs']
        
        assert len(logs) == 1
        assert logs[0]['message'] == 'Test log 1'
        assert logs[0]['level'] == 'INFO'
        assert logs[0]['category'] == 'test'
        assert logs[0]['date'] == '2023-05-01T12:00:00'


@pytest.mark.asyncio
async def test_get_logs_with_s3(es_client_mock, s3_client_mock):
    # Mock Elasticsearch response (empty)
    es_response = {
        '_scroll_id': 'mock_scroll_id',
        'hits': {
            'hits': []
        }
    }
    
    # Mock S3 response
    s3_log = {
        'message': 'S3 Test log',
        'level': 'DEBUG',
        'category': 's3_test',
        'date': '2023-04-20T10:00:00'
    }
    s3_response = MagicMock()
    s3_response['Body'].readline.side_effect = [
        json.dumps(s3_log).encode(),
        b''
    ]
    
    with patch('logs.get_logs_handler._get_logs_from_elasticsearch', return_value=es_response), \
         patch('logs.get_logs_handler._scroll_logs_from_elasticsearch', return_value={'hits': {'hits': []}}), \
         patch('aiobotocore.get_session') as mock_get_session, \
         patch('logs.get_logs_handler.SNAPSHOT_DAYS_FROM_NOW', 20):
        
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_session.create_client.return_value = s3_client_mock
        s3_client_mock.get_object.return_value = s3_response
        
        request = make_mocked_request('GET', '/logs/1/2023-04-20-00-00-00/2023-04-20-23-59-59')
        response = await get_logs(request, es_client_mock)
        
        assert isinstance(response, web.StreamResponse)
        content = await response.text()
        logs = json.loads(content)['logs']
        
        assert len(logs) == 1
        assert logs[0]['message'] == 'S3 Test log'
        assert logs[0]['level'] == 'DEBUG'
        assert logs[0]['category'] == 's3_test'
        assert logs[0]['date'] == '2023-04-20T10:00:00'


@pytest.mark.asyncio
async def test_get_logs_no_results(es_client_mock):
    # Mock Elasticsearch response (empty)
    es_response = {
        '_scroll_id': 'mock_scroll_id',
        'hits': {
            'hits': []
        }
    }
    
    with patch('logs.get_logs_handler._get_logs_from_elasticsearch', return_value=es_response), \
         patch('logs.get_logs_handler._scroll_logs_from_elasticsearch', return_value={'hits': {'hits': []}}), \
         patch('aiobotocore.get_session') as mock_get_session, \
         patch('logs.get_logs_handler.SNAPSHOT_DAYS_FROM_NOW', 0):
        
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_session.create_client.return_value = MagicMock()
        
        request = make_mocked_request('GET', '/logs/1/2023-05-01-00-00-00/2023-05-01-23-59-59')
        response = await get_logs(request, es_client_mock)
        
        assert isinstance(response, web.StreamResponse)
        content = await response.text()
        logs = json.loads(content)['logs']
        
        assert len(logs) == 0
