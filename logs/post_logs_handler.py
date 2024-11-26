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
    Handle POST request to save logs into ElasticSearch.
    
    This function processes incoming log data, formats it for ElasticSearch,
    and bulk inserts the logs into the appropriate index.
    '''
    # Extract log data from the request
    data = await request.json()
    logs = data['logs']

    # Get the service ID from the URL parameters
    service_id = request.match_info.get('id')

    for log in logs:
        # Generate the index name based on the log date and service ID
        log_date = datetime.utcfromtimestamp(float(log['date']))
        index = log_date.strftime('data-{}-%Y-%m-%d'.format(service_id))

        # Update the log entry with additional metadata
        log.update(
            {
                '_type': 'logs',
                'service_id': service_id,
            }
        )
        # Set the ElasticSearch index and convert the date to datetime object
        log['_index'] = index
        log['date'] = log_date

    # Bulk insert the processed logs into ElasticSearch
    helpers.bulk(
        es_client,
        logs,
        index=index,
    )

    return web.Response()
