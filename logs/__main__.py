'''
Logs Main Module

This module is the entry point for the Logs. It sets up the web application,
configures routes for handling log operations, and starts the service.

The service provides two main endpoints:
1. POST /api/1/service/{id}/logs - for posting new logs
2. GET /api/1/service/{id}/logs/{start}/{end} - for retrieving logs within a time range

The service uses Elasticsearch as its backend for storing and retrieving logs.
'''

from functools import partial
from aiohttp import web
from elasticsearch import Elasticsearch

from logs.post_logs_handler import post_logs
from logs.get_logs_handler import get_logs

from logs.config import ELASTICSEARCH_HOSTNAME
from logs.config import AIOHTTP_PORT


def main():
    '''
    Service starting function.
    '''
    app = web.Application()

    es_client = Elasticsearch(hosts=[ELASTICSEARCH_HOSTNAME],)

    app.router.add_post(
        '/api/1/service/{id}/logs',
        partial(
            post_logs,
            es_client=es_client,
        )
    )

    app.router.add_get(
        '/api/1/service/{id}/logs/{start}/{end}',
        partial(
            get_logs,
            es_client=es_client,
        )
    )

    web.run_app(
        app,
        port=AIOHTTP_PORT,
    )


if __name__ == '__main__':
    main()
