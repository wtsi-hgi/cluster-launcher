import json

import asyncio
import subprocess
from aiohttp import web
from concurrent.futures import ThreadPoolExecutor

import routes



async def shutdown(app):
  app["pool"].shutdown()

if __name__ == '__main__':
  app = web.Application()

  app.on_shutdown.append(shutdown)

  #loop = asyncio.get_event_loop()

  app["jobs"] = {}
  app["pool"] = ThreadPoolExecutor(max_workers=5)
  app["status"] = ""

  routes.assign_routes(app)
  web.run_app(app, port=5000)
