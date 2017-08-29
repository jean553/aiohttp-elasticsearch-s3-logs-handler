'''
This script is used for tests purposes only.

Execute massive amount of POST logs in order to monitor
how the service reacts when a lot of writte requests are performed.

Logs are sent per one minute slices.
In order to generate a lot of requests,
POST requests are performed asynchronously.
'''

import os
import csv

import asyncio
import aiohttp

POST_LOGS_ENDPOINT = 'http://localhost:8000/api/1/service/1/logs'
TSV_FILES_DIRECTORY = '/vagrant/tests/performance/files/'

# 2017-08-29 12:00 to 13:00
START_TIMESTAMP = 1504008000
END_TIMESTAMP = 1504011600

SECONDS_INTERVAL = 60


async def send_data(json):
    '''
    Posts data to the service.

    Args:
        json(dict): json data to send
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

    logs_files = os.listdir(TSV_FILES_DIRECTORY)
    loop = asyncio.get_event_loop()

    start_timestamp = START_TIMESTAMP
    end_timestamp = start_timestamp + SECONDS_INTERVAL

    while start_timestamp < END_TIMESTAMP:

        for file_path in logs_files:

            with open(TSV_FILES_DIRECTORY + file_path) as logs_file:

                csv_reader = csv.reader(
                    logs_file,
                    delimiter='\t',
                )

                logs = list()

                for line in csv_reader:

                    # TODO: #46 investigate why should I do this
                    # as we iterate over the CSV reader
                    log = line[0].split()

                    timestamp = int(log[1])

                    if (
                        timestamp < start_timestamp or
                        timestamp >= end_timestamp
                    ):
                        continue

                    logs.append({
                        'date': timestamp,
                        'level': log[2],
                        'category': log[3],
                        'message': log[4],
                    })

                json = {'logs': logs}

                if logs:
                    loop.run_until_complete(send_data(json))

        start_timestamp += SECONDS_INTERVAL
        end_timestamp += SECONDS_INTERVAL


if __name__ == '__main__':
    main()
