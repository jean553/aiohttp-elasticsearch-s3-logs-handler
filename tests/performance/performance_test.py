'''
This script is used for tests purposes only.

Execute massive amount of POST logs in order to monitor
how the service reacts when a lot of writte requests are performed.

Logs are sent per one minute slices.
In order to generate a lot of requests,
POST requests are performed asynchronously.
'''

import csv

import asyncio
import aiohttp

POST_LOGS_ENDPOINT = 'http://localhost:8000/api/1/service/1/logs'
TSV_FILES_DIRECTORY = '/vagrant/tests/performance/files/'


async def send_data(json):
    '''
    Posts data to the service.

    Args:
        json(dict) json data to send
    '''
    async with aiohttp.ClientSession() as session:
        async with session.post(
            POST_LOGS_ENDPOINT,
            json=json,
        ) as response:
            await response.text()


def main():
    '''
    Script entry point.
    '''

    # FIXME: #44 takes a specific file for development purposes;
    # should browse a folder and take all TSV files inside.
    file_path = TSV_FILES_DIRECTORY + '1.tsv'

    with open(file_path) as logs_file:

        # FIXME: #45 we read the whole file for now,
        # but we should only read one minute of logs
        csv_reader = csv.reader(
            logs_file,
            delimiter='\t',
        )

        logs = list()

        for line in csv_reader:

            # TODO: #46 investigate why should I do this
            # as we iterate over the CSV reader
            log = line[0].split()

            logs.append({
                'date': log[1],
                'level': log[2],
                'category': log[3],
                'message': log[4],
            })

        json = {'logs': logs}

    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_data(json))


if __name__ == '__main__':
    main()
