from aiohttp import web
import asyncio
import json

import routes
import subprocess

if __name__ == '__main__':
    app = web.Application()

    loop = asyncio.get_event_loop()

    routes.assign_routes(app)

    web.run_app(app, port=5000)
