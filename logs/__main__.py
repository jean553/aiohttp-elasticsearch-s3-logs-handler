'''
Starts the service.
'''
=> This project implements an asynchronous non-blocking logs handler
=> using Elasticsearch for short-term storage and Amazon S3 for long-term storage.
=> It provides API endpoints to:
=>  1. Post logs to Elasticsearch
=>  2. Retrieve logs from Elasticsearch or S3 based on date range
=> end of the comment

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
