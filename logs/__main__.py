'''
__main__.py

This module is the entry point for the logs service.
It sets up the aiohttp web application and defines the routes.
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
    Sets up the aiohttp web application, configures routes, and starts the server.
    '''
    app = web.Application()

    # Initialize Elasticsearch client
    es_client = Elasticsearch(hosts=[ELASTICSEARCH_HOSTNAME],)

    # Configure routes
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

    # Start the web server
    web.run_app(
        app,
        port=AIOHTTP_PORT,
    )


if __name__ == '__main__':
    main()
