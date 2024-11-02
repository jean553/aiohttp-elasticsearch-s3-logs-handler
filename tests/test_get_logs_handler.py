import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from logs.get_logs_handler import get_logs


class TestGetLogsHandler(AioHTTPTestCase):
    async def get_application(self):
        app = web.Application()
        app.router.add_get('/logs/{id}/{start}/{end}', get_logs)
        return app

    @patch('logs.get_logs_handler._get_logs_from_elasticsearch')
    @patch('logs.get_logs_handler._scroll_logs_from_elasticsearch')
    @unittest_run_loop
    async def test_get_logs_from_elasticsearch(self, mock_scroll, mock_get_logs):
        # Mock Elasticsearch response
        mock_get_logs.return_value = {
            '_scroll_id': 'test_scroll_id',
            'hits': {
                'hits': [
                    {'_source': {'message': 'Test log 1', 'date': '2023-05-01T12:00:00'}},
                    {'_source': {'message': 'Test log 2', 'date': '2023-05-01T13:00:00'}},
                ]
            }
        }
        mock_scroll.return_value = {'_scroll_id': 'test_scroll_id', 'hits': {'hits': []}}

        # Make request
        resp = await self.client.get('/logs/1/2023-05-01-00-00-00/2023-05-01-23-59-59')
        assert resp.status == 200

        # Check response content
        content = await resp.text()
        assert '"message": "Test log 1"' in content
        assert '"message": "Test log 2"' in content

    @patch('logs.get_logs_handler._get_logs_from_elasticsearch')
    @patch('logs.get_logs_handler._scroll_logs_from_elasticsearch')
    @patch('aiobotocore.get_session')
    @unittest_run_loop
    async def test_get_logs_from_s3(self, mock_s3_session, mock_scroll, mock_get_logs):
        # Mock Elasticsearch response (empty)
        mock_get_logs.return_value = {'_scroll_id': 'test_scroll_id', 'hits': {'hits': []}}
        mock_scroll.return_value = {'_scroll_id': 'test_scroll_id', 'hits': {'hits': []}}

        # Mock S3 response
        mock_s3_client = MagicMock()
        mock_s3_session.return_value.create_client.return_value = mock_s3_client
        mock_s3_client.get_object.return_value = {
            'Body': MagicMock(
                readline=MagicMock(side_effect=[
                    b'{"message": "S3 log 1", "date": "2023-04-20T12:00:00"}\n',
                    b'{"message": "S3 log 2", "date": "2023-04-20T13:00:00"}\n',
                    b''
                ])
            )
        }

        # Make request
        resp = await self.client.get('/logs/1/2023-04-20-00-00-00/2023-04-20-23-59-59')
        assert resp.status == 200

        # Check response content
        content = await resp.text()
        assert '"message": "S3 log 1"' in content
        assert '"message": "S3 log 2"' in content

    @patch('logs.get_logs_handler._get_logs_from_elasticsearch')
    @patch('logs.get_logs_handler._scroll_logs_from_elasticsearch')
    @unittest_run_loop
    async def test_get_logs_empty_response(self, mock_scroll, mock_get_logs):
        # Mock empty Elasticsearch response
        mock_get_logs.return_value = {'_scroll_id': 'test_scroll_id', 'hits': {'hits': []}}
        mock_scroll.return_value = {'_scroll_id': 'test_scroll_id', 'hits': {'hits': []}}

        # Make request
        resp = await self.client.get('/logs/1/2023-05-01-00-00-00/2023-05-01-23-59-59')
        assert resp.status == 200

        # Check response content
        content = await resp.text()
        assert content == '{"logs": []}'


if __name__ == '__main__':
    unittest.main()
