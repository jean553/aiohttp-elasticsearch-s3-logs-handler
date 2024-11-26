'''
Handles POST /logs requests.
This module contains the handler for posting logs to ElasticSearch.
'''
from datetime import datetime
from elasticsearch import Elasticsearch, helpers

from aiohttp import web


async def post_logs(
    request: web.Request,
    es_client: Elasticsearch,
):
    '''
    Handler for POST /logs/{id} endpoint.
    Receives logs from a service and saves them into ElasticSearch.
    '''

    request_data = await request.json()
    logs_to_save = request_data['logs']

    service_id = request.match_info.get('id')

    for log_entry in logs_to_save:

        # TODO: #125 almost everytime, indices have the same day,
        # so this is superfluous to generate the index for each log;
        # we should find a better way to handle indices creations
        log_timestamp = datetime.utcfromtimestamp(float(log_entry['date']))
        elasticsearch_index = log_timestamp.strftime('data-{}-%Y-%m-%d'.format(service_id))

        log_entry.update(
            {
                '_type': 'logs',
                'service_id': service_id,
            }
        )
        log_entry['_index'] = elasticsearch_index
        log_entry['date'] = log_timestamp

    helpers.bulk(
        es_client,
        logs_to_save,
        index=elasticsearch_index,
    )

    return web.Response()
