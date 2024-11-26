import pytest
from aiohttp import web
from unittest.mock import MagicMock, patch
from elasticsearch import Elasticsearch

from logs.post_logs_handler import post_logs
from logs.get_logs_handler import get_logs

@pytest.fixture
def es_client():
    return MagicMock(spec=Elasticsearch)

@pytest.fixture
async def client(aiohttp_client, es_client):
    app = web.Application()
    app.router.add_post('/api/1/service/{id}/logs', post_logs)
    app.router.add_get('/api/1/service/{id}/logs/{start}/{end}', get_logs)
    app['es_client'] = es_client
    return await aiohttp_client(app)

async def test_post_logs(client, es_client):
    test_logs = {
        'logs': [
            {
                'message': 'Test log message',
                'level': 'INFO',
                'category': 'Test',
                'date': '1609459200'
            }
        ]
    }
    
    resp = await client.post('/api/1/service/1/logs', json=test_logs)
    assert resp.status == 200
    
    es_client.bulk.assert_called_once()
    call_args = es_client.bulk.call_args[0][1]
    assert len(call_args) == 1
    assert call_args[0]['_index'].startswith('data-1-')
    assert call_args[0]['service_id'] == '1'
    assert call_args[0]['message'] == 'Test log message'

async def test_get_logs(client, es_client):
    es_client.search.return_value = {
        '_scroll_id': 'test_scroll_id',
        'hits': {
            'hits': [
                {
                    '_source': {
                        'message': 'Test log message',
                        'level': 'INFO',
                        'category': 'Test',
                        'date': '2021-01-01T00:00:00',
                        'service_id': '1'
                    }
                }
            ]
        }
    }
    es_client.scroll.return_value = {'hits': {'hits': []}}
    
    resp = await client.get('/api/1/service/1/logs/2021-01-01-00-00-00/2021-01-01-23-59-59')
    assert resp.status == 200
    
    body = await resp.json()
    assert 'logs' in body
    assert len(body['logs']) == 1
    assert body['logs'][0]['message'] == 'Test log message'

    es_client.search.assert_called_once()
    es_client.scroll.assert_called_once()

if __name__ == '__main__':
    pytest.main()
