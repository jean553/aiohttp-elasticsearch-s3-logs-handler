"""POST logs handler
"""
from datetime import datetime
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
        logs = json.loads(self.request.body.decode('utf-8'))['logs']

        date = datetime.now()
        index = date.strftime('data-%Y-%m-%d-%H')

        for log in logs:
            log.update({'_type': 'logs'})
            log['_index'] = index
            log['date'] = datetime.utcfromtimestamp(float(log['date']))

        helpers.bulk(
            self.es_client,
            logs,
            index=index,
        )
