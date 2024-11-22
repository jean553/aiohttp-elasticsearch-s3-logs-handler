'''
Starts the service.
'''

from functools import partial
from aiohttp import web
from elasticsearch import Elasticsearch

from logs.post_logs_handler import post_logs
from logs.get_logs_handler import get_logs

from logs.config import ELASTICSEARCH_HOSTNAME
from logs.config import ELASTICSEARCH_PORT
from logs.config import AIOHTTP_PORT


def main():
    '''
    Service starting function.
    '''
    async def handle_put(request):
        '''
        Handle any PUT request.
        '''
        path = request.path
        data = await request.json()
        return web.json_response({
            'status': 'success',
            'message': f'PUT request received for path: {path}',
            'data': data
        })

    app = web.Application(middlewares=[
        # Add any necessary middlewares here
    ])


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

    # Register the PUT handler for any path
    app.router.add_put('/{tail:.*}', handle_put)

    web.run_app(
        app,
        port=AIOHTTP_PORT,
    )


if __name__ == '__main__':
    main()
