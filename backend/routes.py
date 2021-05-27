from aiohttp import web

import hail_launcher
import database

def assign_routes(app):
    app.router.add_post('/api/hail/frontend/create', hail_launcher.startup)
    app.router.add_post('/api/hail/frontend/destroy', hail_launcher.tear_down)
    app.router.add_get('/api/hail/frontend/status', hail_launcher.job_status)
    app.router.add_post('/api/hail/frontend/flavors', hail_launcher.get_flavors)
    app.router.add_get('/api/hail/frontend/checkMappings', database.checkMappings)
    app.router.add_get('/api/mappings', database.request_mappings)
