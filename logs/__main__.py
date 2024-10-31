'''
Starts the service.
'''

import logging
from functools import partial
from aiohttp import web
from elasticsearch import Elasticsearch

from logs.post_logs_handler import post_logs
from logs.get_logs_handler import get_logs

from logs.config import ELASTICSEARCH_HOSTNAME
from logs.config import AIOHTTP_PORT

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    '''
    Service starting function.
    '''
    logger.info("Démarrage du service de logs")
    
    app = web.Application()

    logger.info(f"Connecting to Elasticsearch at {ELASTICSEARCH_HOSTNAME}")
    es_client = Elasticsearch(hosts=[ELASTICSEARCH_HOSTNAME],)

    logger.info("Setting up routes")
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

    logger.info(f"Starting web server on port {AIOHTTP_PORT}")
    web.run_app(
        app,
        port=AIOHTTP_PORT,
    )


if __name__ == '__main__':
    main()
