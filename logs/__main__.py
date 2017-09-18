'''
Starts the service.
'''

from aiohttp import web

# TODO: #99 tornado must be replaced by asyncio,
# after that, the module can be renamed back to `logs`
from logs.post_logs_handler import post_logs
from logs.get_logs_handler import get_logs


def main():
    '''
    Service starting function.
    '''
    app = web.Application()

    app.router.add_post(
        '/api/1/service/{id}/logs',
        post_logs,
    )

    app.router.add_get(
        '/api/1/service/{id}/logs/{start}/{end}',
        get_logs,
    )

    # TODO: #93 the port should be an environment variable
    web.run_app(
        app,
        port=8000,
    )


if __name__ == '__main__':
    main()
