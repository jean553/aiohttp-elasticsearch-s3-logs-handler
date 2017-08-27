#!/usr/bin/python
'''
Creates a snapshot of for one index.
'''
import os
import requests

ELASTICSEARCH_ENDPOINT = 'http://elasticsearch:9200'
SNAPSHOTS_DIRECTORY = '/tmp/snapshots'


def get_data_indices():
    '''
    Returns the list of data indices (data-* format).

    Returns:
        (list) list of indices names
    '''
    indices = requests.get(ELASTICSEARCH_ENDPOINT + '/_aliases')
    return [
        index
        for index
        in indices.json()
        if index[:1] != '.'
    ]


def generate_snapshot(index_name):
    '''
    Generate the dump for the given index
    and stores it into the snapshots directory.

    Args:
        index_name(str) name of the index
    '''
    os.system(
        '''
        elasticdump \
            --input=%(elasticsearch_endpoint)s/%(index_name)s \
            --output=%(snapshots_directory)s/%(index_name)s \
            --type=data
        ''' % ({
            'index_name': index_name,
            'snapshots_directory': SNAPSHOTS_DIRECTORY,
            'elasticsearch_endpoint': ELASTICSEARCH_ENDPOINT,
        })
    )


def main():
    '''
    Script entry point.
    '''

    indices = get_data_indices()

    for index in indices:
        generate_snapshot(index)


if __name__ == '__main__':
    main()
