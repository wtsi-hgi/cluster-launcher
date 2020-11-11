from aiohttp import web

async def response(app):
    data = {'some': 'data'}
    return web.Response(text="OK") 

