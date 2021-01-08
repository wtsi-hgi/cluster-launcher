from network import create
from network import destroy

from aiohttp import web
from os import path
import asyncio
import openstack
import os.path
import subprocess

username="an12"


async def handler(request):
  attributes = await request.json()
  print(attributes)

  with open('public_key.pub', 'w') as key_file:
    key_file.write(attributes["public_key"])

  credentials = get_credentials()
  conn = openstack.connect(**credentials)

  if attributes["status"] == False:
    if path.exists('/backend/clusters/'+username):
      print("A cluster is already registered - an error has occured!")
    else:
      create_network(conn)
      subprocess.run(['bash', 'user-creation.sh', username, attributes["password"]])
  else:
    if path.exists('/backend/clusters/'+username):
      subprocess.run(['bash', 'cluster-deletion.sh', username])
      destroy_network(conn)
    else:
      print("No cluster exists - an error has occured")

  return web.Response(text="Received")

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        print(f'[stdout]\n{stdout.decode()}')
    if stderr:
        print(f'[stderr]\n{stderr.decode()}')



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
