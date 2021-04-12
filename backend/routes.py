from aiohttp import web

import hail_launcher

def assign_routes(app):
    app.router.add_post('/api/hail/frontend/create', hail_launcher.startup)
    app.router.add_post('/api/hail/frontend/destroy', hail_launcher.tear_down)
    app.router.add_get('/api/hail/frontend/status', hail_launcher.job_status)
