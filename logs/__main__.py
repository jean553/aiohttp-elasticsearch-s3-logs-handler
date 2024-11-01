'''
Starts the service.
'''

from functools import partial
from aiohttp import web
import os

from logs.post_logs_handler import post_logs
from logs.get_logs_handler import get_logs

def main():
    '''
    Service starting function.
    '''
    app = web.Application()

    es_client = Elasticsearch(hosts=[os.environ.get('ELASTICSEARCH_HOSTNAME', 'localhost')],)

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
        port=int(os.environ.get('AIOHTTP_PORT', 8000)),
    )


if __name__ == '__main__':
    main()
