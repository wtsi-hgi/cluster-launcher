
from aiohttp import web
import json

async def response(app):
    data = {'some': 'datas'}
    txt = '[' + json.dumps(data) + ']'
    return web.Response(text=txt)

