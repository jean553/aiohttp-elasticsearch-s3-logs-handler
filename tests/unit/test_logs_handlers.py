import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from aiohttp import web
from elasticsearch import Elasticsearch

from logs.post_logs_handler import post_logs
from logs.get_logs_handler import get_logs

@pytest.fixture
def es_client():
    return Mock(spec=Elasticsearch)

@pytest.mark.asyncio
async def test_post_logs(es_client):
    mock_request = Mock(spec=web.Request)
    mock_request.match_info = {'id': '123'}
    mock_request.json.return_value = {
        'logs': [
            {
                'message': 'Test log',
                'level': 'INFO',
                'category': 'test',
                'date': '1609459200'
            }
        ]
    }

    with patch('logs.post_logs_handler.helpers.bulk') as mock_bulk:
        response = await post_logs(mock_request, es_client)

    assert isinstance(response, web.Response)
    assert response.status == 200
    mock_bulk.assert_called_once()

@pytest.mark.asyncio
async def test_get_logs(es_client):
    mock_request = Mock(spec=web.Request)
    mock_request.match_info = {
        'id': '123',
        'start': '2021-01-01-00-00-00',
        'end': '2021-01-02-00-00-00'
    }

    with patch('logs.get_logs_handler._get_logs_from_elasticsearch') as mock_get_logs, \
         patch('logs.get_logs_handler._scroll_logs_from_elasticsearch') as mock_scroll_logs:
        
        mock_get_logs.return_value = {
            '_scroll_id': 'test_scroll_id',
            'hits': {
                'hits': [
                    {
                        '_source': {
                            'message': 'Test log',
                            'level': 'INFO',
                            'category': 'test',
                            'date': '2021-01-01T12:00:00'
                        }
                    }
                ]
            }
        }
        mock_scroll_logs.return_value = {'hits': {'hits': []}}

        response = await get_logs(mock_request, es_client)

    assert isinstance(response, web.StreamResponse)
    assert response.content_type == 'application/json'
    
    # We can't easily assert the content of the StreamResponse,
    # but we can check that the coroutines were called
    mock_get_logs.assert_called_once()
    mock_scroll_logs.assert_called_once()

if __name__ == '__main__':
    pytest.main()
