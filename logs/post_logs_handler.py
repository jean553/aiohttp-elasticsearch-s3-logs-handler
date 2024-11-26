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
    Save sent logs into ElasticSearch.
    '''
    # Extract JSON data from the request body
    data = await request.json()
    logs = data['logs']

    # Get the service ID from the URL parameters
    service_id = request.match_info.get('id')

    for log in logs:
        # Convert the log timestamp to a datetime object
        log_date = datetime.utcfromtimestamp(float(log['date']))
        
        # Generate the index name based on the service ID and date
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

    # Return an empty response with a 200 OK status
    return web.Response()
