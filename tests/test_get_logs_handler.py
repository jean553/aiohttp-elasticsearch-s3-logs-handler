import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import web
from elasticsearch import Elasticsearch

from logs.get_logs_handler import get_logs, SNAPSHOT_DAYS_FROM_NOW

@pytest.fixture
def es_client():
    return MagicMock(spec=Elasticsearch)

@pytest.fixture
def mock_request():
    request = MagicMock()
    request.match_info = {
        'id': '1',
        'start': '2023-05-01-00-00-00',
        'end': '2023-05-02-00-00-00'
    }
    return request

@pytest.mark.asyncio
async def test_get_logs_from_elasticsearch(es_client, mock_request):
    mock_es_response = {
        '_scroll_id': 'mock_scroll_id',
        'hits': {
            'hits': [
                {'_source': {'message': 'Test log 1', 'date': '2023-05-01T12:00:00'}},
                {'_source': {'message': 'Test log 2', 'date': '2023-05-01T13:00:00'}}
            ]
        }
    }
    
    with patch('logs.get_logs_handler._get_logs_from_elasticsearch', AsyncMock(return_value=mock_es_response)), \
         patch('logs.get_logs_handler._scroll_logs_from_elasticsearch', AsyncMock(return_value={'hits': {'hits': []}})):
        
        response = await get_logs(mock_request, es_client)
        
        assert isinstance(response, web.StreamResponse)
        assert response.content_type == 'application/json'
        
        # Convert the streamed response to a string
        response_text = ''
        async for data in response.content:
            response_text += data.decode('utf-8')
        
        assert '"logs": [' in response_text
        assert 'Test log 1' in response_text
        assert 'Test log 2' in response_text
        assert response_text.endswith(']}')

@pytest.mark.asyncio
async def test_get_logs_from_s3(es_client, mock_request):
    # Set the start date to be older than SNAPSHOT_DAYS_FROM_NOW
    old_start_date = (datetime.now() - timedelta(days=SNAPSHOT_DAYS_FROM_NOW + 1)).strftime('%Y-%m-%d-%H-%M-%S')
    mock_request.match_info['start'] = old_start_date
    
    mock_es_response = {'_scroll_id': 'mock_scroll_id', 'hits': {'hits': []}}
    mock_s3_response = MagicMock()
    mock_s3_response['Body'].readline = AsyncMock(side_effect=[
        b'{"message": "S3 log 1", "date": "2023-04-20T12:00:00"}\n',
        b'{"message": "S3 log 2", "date": "2023-04-20T13:00:00"}\n',
        b''
    ])
    
    with patch('logs.get_logs_handler._get_logs_from_elasticsearch', AsyncMock(return_value=mock_es_response)), \
         patch('logs.get_logs_handler._scroll_logs_from_elasticsearch', AsyncMock(return_value={'hits': {'hits': []}})), \
         patch('aiobotocore.get_session') as mock_get_session:
        
        mock_s3_client = AsyncMock()
        mock_s3_client.get_object.return_value = mock_s3_response
        mock_get_session.return_value.create_client.return_value = mock_s3_client
        
        response = await get_logs(mock_request, es_client)
        
        assert isinstance(response, web.StreamResponse)
        assert response.content_type == 'application/json'
        
        response_text = ''
        async for data in response.content:
            response_text += data.decode('utf-8')
        
        assert '"logs": [' in response_text
        assert 'S3 log 1' in response_text
        assert 'S3 log 2' in response_text
        assert response_text.endswith(']}')

@pytest.mark.asyncio
async def test_get_logs_empty_result(es_client, mock_request):
    mock_es_response = {'_scroll_id': 'mock_scroll_id', 'hits': {'hits': []}}
    
    with patch('logs.get_logs_handler._get_logs_from_elasticsearch', AsyncMock(return_value=mock_es_response)), \
         patch('logs.get_logs_handler._scroll_logs_from_elasticsearch', AsyncMock(return_value={'hits': {'hits': []}})):
        
        response = await get_logs(mock_request, es_client)
        
        assert isinstance(response, web.StreamResponse)
        assert response.content_type == 'application/json'
        
        response_text = ''
        async for data in response.content:
            response_text += data.decode('utf-8')
        
        assert response_text == '{"logs": []}'

@pytest.mark.asyncio
async def test_get_logs_invalid_date_range(es_client):
    invalid_request = MagicMock()
    invalid_request.match_info = {
        'id': '1',
        'start': '2023-05-02-00-00-00',
        'end': '2023-05-01-00-00-00'  # End date before start date
    }
    
    with pytest.raises(web.HTTPBadRequest):
        await get_logs(invalid_request, es_client)

# Add more tests as needed for other scenarios and edge cases
