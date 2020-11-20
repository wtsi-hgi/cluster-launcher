
from aiohttp import web
import json
from novaclient import client


async def response(app):
    data = {'some': 'datas'}
    txt = '[' + json.dumps(data) + ']'
    return web.Response(text=txt, headers={'ACCESS-CONTROL-ALLOW-ORIGIN':'*'})

def getFlavors(app):
    nova = client.Client()
    flavors=nova.flavors.list(detailed=True)
    ListOfFlavors = []
    for flavor in flavors:
        if flavor.id is not None:
            flavorMap = {}
            flavorMap['Id'] = flavor.id
            flavorMap['Name'] = flavor.name
            category = flavor.name.split('.')
            flavorMap['Category'] = category[0]
            ListOfFlavors.append(flavorMap)

    return web.Response(text=json.dumps(ListOfFlavors), headers={'ACCESS-CONTROL-ALLOW-ORIGIN':'*'})
