import json
import subprocess
import time

import asyncio
import openstack
import os
from aiohttp import web
from concurrent.futures import ThreadPoolExecutor
from os import path

import network

DEBUG = True

async def startup(request):
  username = "an12"

  #Attributes returned from the frontend is in the form:
  # {
  #   public_key: String,
  #   workers: String,
  #   password: String,
  #   flavor: String,
  #   status: Boolean
  # }
  attributes = await request.json()

  jobs = request.app["jobs"]
  pool = request.app["pool"]
  print(attributes)

  jobs[job_key(username, "main")] = pool.submit(cluster_creator, request, attributes, username)


  return web.Response(text="Cluster Creation in Progress")


def cluster_creator(request, attributes, username):
  #Request returned from the frontend is in the form:
  # {
  #   public_key: String,
  #   workers: String,
  #   password: String,
  #   flavor: String,
  #   status: Boolean
  # }

  jobs = request.app["jobs"]
  pool = request.app["pool"]

  print(attributes)

  with open('public_key.pub', 'w') as key_file:
    key_file.write(attributes["public_key"])

  credentials = get_credentials()
  conn = openstack.connect(**credentials)

  flavors=conn.list_flavors()
  flavor_names = [str(flavor.name) for flavor in flavors if flavor.id is not None]

  if attributes["flavor"] in flavor_names:
    print(attributes["flavor"])
  else:
    print("Invalid Flavor - Switching to default")
    attributes["flavor"] = "m2.medium"

  if attributes["status"] == False:
    if path.exists('/backend/clusters/'+username):
      print("A cluster is already registered - an error has occured!")
    else:
      request.app["status"]="UP"
      create_network(conn, username)
      #Job Tuple for launching clusters. Useful for checking status of jobs and their state
      jobs[job_key(username, "cluster")] =( pool.submit(run, ['bash', 'cluster-creation.sh', username, attributes["password"], attributes["workers"], attributes["flavor"]]),
         "UP")
      if DEBUG:
        print(jobs[job_key(username, "cluster")][0].result())
      print("Cluster Creation in Progress")



async def tear_down(request):
  #Request returned from the frontend is in the form:
  # {
  #   status: Boolean
  # }
  attributes = await request.json()
  print(attributes)

  username = "an12"

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
      output = pool.submit(destroy_network, conn, username)
      print("Cluster Deletion in Progress")

    else:
      print("No cluster exists - an error has occured")

  return web.Response(text="Cluster Deletion in Progress")


async def job_status(request):
  jobs = request.app["jobs"]

  username = "an12"

  credentials = get_credentials()
  conn = openstack.connect(**credentials)
  print(request)
  path_to_cluster_ip = '/backend/clusters/' + username + '/osdataproc/terraform/terraform.tfstate.d/' + username + '/outputs.json'

  # In the event of the container going down and being brought back up, jobs will be empty
  # This catches clusters if they're up in this eventuality
  if username not in jobs:
    if path.exists(path_to_cluster_ip):
      with open(path_to_cluster_ip) as json_file:
        data = json.load(json_file)
        cluster_ip = data["spark_master_public_ip"]["value"]
      # Returns this response if the cluster is up
      return web.json_response({
        "status": "up",
        "cluster_ip": cluster_ip
      })
    else:
      print("Cannot find path to cluster ip")
      # Returns this response if the cluster is down
      return web.json_response({
        "status": "down"
      })

  else:
    job = jobs[username][0]
    if job.done():
      # Returns this response if the cluster is up
      if jobs[username][1] == "UP":
        print(jobs[username][1])
        with open(path_to_cluster_ip) as json_file:
          data = json.load(json_file)
          cluster_ip = data["spark_master_public_ip"]["value"]
        return web.json_response({
          "status": "up",
          "cluster_ip": cluster_ip
        })

      # Returns this response if the cluster is down
      elif jobs[username][1] == "DOWN":
        print(jobs[username][1])
        return web.json_response({
          "status": "down"
        })

    # Returns this response if the cluster is in a pending state
    # The "pending" attribute determines whether the cluster is in a UP or DOWN pending phase
    if job.running():
      return web.json_response({
        "status": "pending",
        "pending": jobs[username][1]
      })

# This function is passed to the Thread Pool for running the bash scripts async
def run(cmd):
  return subprocess.run(cmd, capture_output=True, text=True)

def job_key(user, job_type):
  return f"{user}.{job_type}"

def create_network(conn, username):
  network_name = username+"-cluster-network"
  network_list = [network.name for network in conn.network.networks()]

  if network_name in network_list:
    print("Network Exists")
  else:
    network.create(username)

def destroy_network(conn, username):
  prefix = username+"-cluster"
  network_name = prefix + "-network"

  network_list = [network.name for network in conn.network.networks()]

  if network_name in network_list:
    time.sleep(200)
    network.destroy(username)
  else:
    print("Network doesn't exist")


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
