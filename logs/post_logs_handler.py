"""POST logs handler
"""
import datetime
import json
import tornado.web
from elasticsearch import helpers

class PostLogsHandler(tornado.web.RequestHandler):
    """Post logs handler.
    """

    def initialize(
        self,
        es_client,
    ):
        """Initializes the received request handling process.
        """
        self.es_client = es_client

    def post(self):
        """Post /logs action.
        """
        data = json.loads(self.request.body.decode('utf-8'))

        date = datetime.datetime.now()
        index = date.strftime('data-%Y-%m-%d-%H')

        log_date = datetime.datetime.utcfromtimestamp(float(data['date']))

        helpers.bulk(
            self.es_client,
            [{
                '_type': 'data',
                '_index': index,
                'date': log_date,
                'message': data['message'],
                'category': data['category'],
                'level': data['level'],
            }],
        )
