from aiohttp import web

import communicator


def assign_routes(app):
    app.router.add_get('/hail/backend', communicator.response)
