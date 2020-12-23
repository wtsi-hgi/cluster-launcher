from network import create
from network import destroy

from aiohttp import web
from os import path
import openstack
import os.path
import subprocess

username="an12"


async def handler(request):
  attributes = await request.json()
  print(attributes["public_key"])

  with open('public_key.pub', 'w') as key_file:
    key_file.write(attributes["public_key"])

  credentials = get_credentials()
  conn = openstack.connect(**credentials)

  if path.exists('/backend/clusters/'+username):
    print("Path exists")
  else:
    create_network(conn)
    subprocess.run(['bash', 'user-creation.sh', username, attributes["password"]])
  #print("Network Created... Deleting Network")
  #destroy_network(conn)

  return web.Response(text="Received")

def create_network(conn):
  network_name = username+"-cluster-network"
  network_list = list_networks(conn)

  if network_name in network_list:
    print("Network Exists")
  else:
    create(username)

def destroy_network(conn):
  prefix = username+"-cluster"
  network_name = prefix + "-network"
  network_list = list_networks(conn)
  if network_name in network_list:
    destroy(username)
  else:
    print("Network doesn't exist")


def list_networks(conn):
  network_list = []
  for network in conn.network.networks():
        network_list.append(network.name)
  return network_list

def get_credentials():
    d = {}
    d['version']  = "2"
    d['username'] = os.environ['OS_USERNAME']
    d['api_key'] = os.environ['OS_PASSWORD']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['project_id'] = os.environ['OS_PROJECT_ID']
    return d
