'''
Elasticsearch client routines for tests
'''


def remove_all_data_indices(es_client):
    '''
    Removes all the data-* indices.

    Args:
        es_client(elasticsearch.client.Elasticsearch)
    '''
    es_client.delete_by_query(
        index='data-*',
        body={},
    )
    es_client.indices.delete(index='data-*')
