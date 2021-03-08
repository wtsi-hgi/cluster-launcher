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
import time

username="an12"
DEBUG = False

async def startup(request):
  attributes = await request.json()
  jobs = request.app["jobs"]
  pool = request.app["pool"]

  print(attributes)

  with open('public_key.pub', 'w') as key_file:
    key_file.write(attributes["public_key"])

  credentials = get_credentials()
  conn = openstack.connect(**credentials)

  flavor_names = (getFlavors(conn))

  if attributes["flavor"] in flavor_names:
    print(attributes["flavor"])
  else:
    print("Invalid Flavor - Switching to default")
    flavor_id = "m2.medium"

  if attributes["status"] == False:
    if path.exists('/backend/clusters/'+username):
      print("A cluster is already registered - an error has occured!")
    else:
      request.app["status"]="UP"
      create_network(conn)
      #Job Tuple for launching clusters. Useful for checking status of jobs and their state
      jobs[username] =( pool.submit(run, ['bash', 'user-creation.sh', username, attributes["password"], attributes["workers"], attributes["flavor"]]),
         "UP")
      if DEBUG:
        print(jobs[username][0].result())
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
      request.app["status"]="DOWN"
      #Job Tuple for destroying clusters. Useful for checking status of jobs and their state
      jobs[username] = ( pool.submit(run, ['bash', 'cluster-deletion.sh', username]), "DOWN")
      if DEBUG:
        print(jobs[username][0].result())
      output = pool.submit(destroy_network, conn)
      print("Cluster Deletion in Progress")

    else:
      print("No cluster exists - an error has occured")

  return web.Response(text="Received")


async def job_status(request):
  jobs = request.app["jobs"]
  credentials = get_credentials()
  conn = openstack.connect(**credentials)
  print(request)
  path_to_cluster_ip = '/backend/clusters/' + username + '/osdataproc/terraform/terraform.tfstate.d/' + username + '/outputs.json'

  if username not in jobs:
    print("Down")
    if path.exists(path_to_cluster_ip):
      with open(path_to_cluster_ip) as json_file:
        data = json.load(json_file)
        cluster_ip = data["spark_master_public_ip"]["value"]
        print(cluster_ip)
      return web.json_response({
        "status": "up",
        "cluster_ip": cluster_ip
      })
    else:
      return web.json_response({
        "status": "down"
      })

  else:
    job = jobs[username][0]

    if job.done():
      if jobs[username][1] == "UP":
        print("UP DONE")
        with open(path_to_cluster_ip) as json_file:
          data = json.load(json_file)
          cluster_ip = data["spark_master_public_ip"]["value"]
        return web.json_response({
          "status": "up",
          "cluster_ip": cluster_ip
        })
      elif jobs[username][1] == "DOWN":
        print("DOWN DONE")
        return web.json_response({
          "status": "down"
        })

    if job.running():
      print("Pending")
      return web.json_response({
        "status": "pending",
        "pending": request.app["status"]
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
    time.sleep(200)
    destroy(username)
  else:
    print("Network doesn't exist")


def list_networks(conn):
  network_list = []

  try:
    for network in conn.network.networks():
        network_list.append(network.name)
  except:
    raise Exception("An issue with connecting to OpenStack has occured when listing networks")
  return network_list

def getFlavors(conn):
    flavors=conn.list_flavors()
    ListOfFlavors = []
    for flavor in flavors:
        if flavor.id is not None:
            #flavorMap = {}
            #flavorMap['Id'] = flavor.id
            #flavorMap['Name'] = flavor.name
            #category = flavor.name.split('.')
            #flavorMap['Category'] = category[0]
            ListOfFlavors.append(str(flavor.name))

    return ListOfFlavors


def get_credentials():
  d = {}
  try:
    d['version']  = "2"
    d['username'] = os.environ['OS_USERNAME']
    d['api_key'] = os.environ['OS_PASSWORD']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['project_id'] = os.environ['OS_PROJECT_ID']
  except KeyError:
    raise Exception("Could not find all required fields in the environment")
  return d
