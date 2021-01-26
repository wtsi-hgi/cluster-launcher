from network import create
from network import destroy

from aiohttp import web
from concurrent.futures import ThreadPoolExecutor
from os import path
import asyncio
import json
import openstack
import os.path
import subprocess

username="an12"

async def startup(request):
  attributes = await request.json()
  jobs = request.app["jobs"]
  pool = request.app["pool"]

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
      jobs[username] = pool.submit(run, ['bash', 'user-creation.sh', username, attributes["password"]])
      print("Cluster Creation in Progress")

  return web.Response(text="Received")


async def tear_down(request):
  attributes = await request.json()
  print(attributes)
  jobs = request.app["jobs"]
  pool = request.app["pool"]

  credentials = get_credentials()
  conn = openstack.connect(**credentials)

  if attributes["status"] == True:
    if path.exists('/backend/clusters/'+username):
      jobs[username] = pool.submit(run, ['bash', 'cluster-deletion.sh', username])
      destroy_network(conn)
      print("Cluster Deletion in Progress")

    else:
      print("No cluster exists - an error has occured")

  return web.Response(text="Received")


async def job_status(request):
  jobs = request.app["jobs"]
  credentials = get_credentials()
  conn = openstack.connect(**credentials)

  if username not in jobs:
    return web.json_response({
      "status": "down"
    })

  else:
    job = jobs[username]

    if job.done():
      path = '/backend/clusters/an12/osdataproc/terraform/terraform.tfstate.d/an12/outputs.json'
      with open(path) as json_file:
        data = json.load(json_file)
        cluster_ip = data["spark_master_public_ip"]["value"]

      return web.json_response({
        "status": "done",
        "cluster_ip": "cluster_ip"
      })

    if job.running():
      return web.json_response({
        "status": "pending"
      })

def run(cmd):
  return subprocess.run(cmd, capture_output=True, text=True)


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
