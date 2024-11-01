from aiohttp import web

async def hello_world(request):
    return web.Response(text='Hello, world!')

def setup_routes(app):
    app.router.add_get('/hello', hello_world)
