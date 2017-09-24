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
    data = await request.json()
    logs = data['logs']

    service_id = request.match_info.get('id')

    for log in logs:

        # TODO: #125 almost everytime, indices have the same day,
        # so this is superfluous to generate the index for each log;
        # we should find a better way to handle indices creations
        log_date = datetime.utcfromtimestamp(float(log['date']))
        index = log_date.strftime('data-{}-%Y-%m-%d'.format(service_id))

        log.update(
            {
                '_type': 'logs',
                'service_id': service_id,
            }
        )
        log['_index'] = index
        log['date'] = log_date

    helpers.bulk(
        es_client,
        logs,
        index=index,
    )

    return web.Response()
