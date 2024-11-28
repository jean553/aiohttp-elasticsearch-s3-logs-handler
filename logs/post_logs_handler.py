'''
Handles POST /logs requests.
'''
from datetime import datetime
from elasticsearch import Elasticsearch, helpers

from aiohttp import web


async def post_logs(
    request: web.Request,
    es_client: Elasticsearch,
):
    '''
    Handle POST request to save logs into Elasticsearch.
    
    This function processes incoming log data, formats it for Elasticsearch,
    and performs a bulk insert operation.
    
    Args:
        request (web.Request): The incoming HTTP request containing log data.
        es_client (Elasticsearch): The Elasticsearch client for data insertion.
    '''
    data = await request.json()
    logs = data['logs']

    service_id = request.match_info.get('id')

    for log in logs:
        # Generate the index name based on the log date and service ID

        # TODO: #125 almost everytime, indices have the same day,
        # so this is superfluous to generate the index for each log;
        # we should find a better way to handle indices creations
        log_date = datetime.utcfromtimestamp(float(log['date']))
        index = log_date.strftime('data-{}-%Y-%m-%d'.format(service_id))

        # Augment each log entry with additional metadata
        log.update(
            {
                '_type': 'logs',
                'service_id': service_id,
            }
        )
        log['_index'] = index
        log['date'] = log_date

    # Perform bulk insert of logs into Elasticsearch
    helpers.bulk(
        es_client,
        logs,
        index=index,
    )

    return web.Response()
