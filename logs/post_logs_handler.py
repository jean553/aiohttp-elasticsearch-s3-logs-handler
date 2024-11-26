'''
post_logs_handler.py

This module handles POST requests to the /logs endpoint.
It receives log data and saves it into ElasticSearch.
'''
from datetime import datetime
from elasticsearch import Elasticsearch, helpers

from aiohttp import web


async def post_logs(
    request: web.Request,
    es_client: Elasticsearch,
):
    '''
    Save sent logs into ElasticSearch.

    Args:
        request (web.Request): The incoming HTTP request
        es_client (Elasticsearch): The Elasticsearch client

    Returns:
        web.Response: An empty response indicating successful operation
    '''
    data = await request.json()
    logs = data['logs']

    service_id = request.match_info.get('id')

    for log in logs:

        # Generate the index name based on the log date
        # TODO: #125 almost everytime, indices have the same day,
        # so this is superfluous to generate the index for each log;
        # we should find a better way to handle indices creations
        log_date = datetime.utcfromtimestamp(float(log['date']))
        index = log_date.strftime('data-{}-%Y-%m-%d'.format(service_id))

        # Add additional metadata to the log
        log.update(
            {
                '_type': 'logs',
                'service_id': service_id,
            }
        )
        log['_index'] = index
        log['date'] = log_date

    # Bulk insert logs into Elasticsearch
    helpers.bulk(
        es_client,
        logs,
        index=index,
    )

    return web.Response()
