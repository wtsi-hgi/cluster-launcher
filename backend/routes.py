from aiohttp import web

import communicator
import hail_launcher

def wait_for_cookie(app):
    app.router.add_get('/hail/frontend', hail_launcher.startup)

def assign_routes(app):
    app.router.add_get('/hail/backend', communicator.response)
    
