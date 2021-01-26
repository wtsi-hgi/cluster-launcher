from aiohttp import web

import communicator
import hail_launcher

def assign_routes(app):
    app.router.add_get('/api/hail/api/flavors/', communicator.getFlavors)
    app.router.add_post('/api/hail/frontend', hail_launcher.startup)
    app.router.add_post('/api/hail/frontend/destroy', hail_launcher.tear_down)
