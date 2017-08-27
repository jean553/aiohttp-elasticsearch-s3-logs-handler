#!/usr/bin/python
'''
Creates a snapshot of for one index.
'''
import requests

ELASTICSEARCH_ENDPOINT = 'http://elasticsearch:9200'


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


def main():
    '''
    Script entry point.
    '''

    indices = get_data_indices()

    # FIXME: only for debug purposes,
    # must be deleted
    for index in indices:
        print(index)


if __name__ == '__main__':
    main()
