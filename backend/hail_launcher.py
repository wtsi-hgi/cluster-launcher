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

DEBUG = False

async def startup(request):
  username = "an12"

  #Request returned from the frontend is in the form:
  # {
  #   public_key: String,
  #   workers: String,
  #   password: String,
  #   flavor: String,
  #   status: Boolean
  # }
  attributes = await request.json()

  #Initialise the Pool and Jobs dictionary as variables
  jobs = request.app["jobs"]
  pool = request.app["pool"]

  #Creates a thread with cluster creation code to prevent blocking the handler
  jobs[username] = ( pool.submit(cluster_creator, request, attributes, username), "UP" )


  return web.Response(text="Cluster Creation in Progress")


def cluster_creator(request, attributes, username):
  #Attributes passed in the form:
  # {
  #   public_key: String,
  #   workers: String,
  #   password: String,
  #   flavor: String,
  #   status: Boolean
  # }

  with open('public_key.pub', 'w') as key_file:
    key_file.write(attributes["public_key"])

  credentials = get_credentials()
  conn = openstack.connect(**credentials)

  flavors=conn.list_flavors()
  flavor_names = [str(flavor.name) for flavor in flavors if flavor.id is not None]

  if attributes["flavor"] not in flavor_names:
    #If the flavor provided by the user is not a valid flavor
    #it'll be switched for m2.medium
    print("Invalid Flavor - Switching to default")
    attributes["flavor"] = "m2.medium"

  if attributes["status"] == False:
    if path.exists('/backend/clusters/'+username):
      #Implement better logging system for errors
      #This error indicates the cluster still exists despite the codebase believing it to be down
      print("A cluster is already registered - an error has occured!")
    else:
      #Creates the user's network
      create_network(conn, username)

      #Run the cluster creation bash script
      subprocess.run(['bash', 'cluster-creation.sh', username, attributes["password"], attributes["workers"], attributes["flavor"]], capture_output=True, text=True)


async def tear_down(request):
  #Request returned from the frontend is in the form:
  # {
  #   status: Boolean
  # }
  attributes = await request.json()

  username = "an12"

  #Initialise the Pool and Jobs dictionary as variables
  jobs = request.app["jobs"]
  pool = request.app["pool"]

  #Start a Thread with cluster deletion code to prevent blocking the handler
  jobs[username] = ( pool.submit(cluster_deletion, request, attributes, username), "DOWN" )

  return web.Response(text="Cluster Deletion in Progress")


def cluster_deletion(request, attributes, username):
  #Take OpenStack credentials from the OS_* environment variables and create a connection object
  credentials = get_credentials()
  conn = openstack.connect(**credentials)

  if attributes["status"] == True:
    if path.exists('/backend/clusters/'+username):
      #Job Tuple for destroying clusters. Useful for checking status of jobs and their state
      subprocess.run(['bash', 'cluster-deletion.sh', username], capture_output=True, text=True)

      destroy_network(conn, username)
      print("Cluster Deletion in Progress")

    else:
      #Improve Logging for Error Messages
      #This error is called if there is no cluster to delete but the backend believes it exists
      print("No cluster exists - an error has occured")


async def job_status(request):
  #Assign the Jobs Dictionary to the variable jobs
  jobs = request.app["jobs"]
  print(jobs)

  username = "an12"
  #Take OpenStack credentials from the OS_* environment variables and create a connection object
  credentials = get_credentials()
  conn = openstack.connect(**credentials)

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
        #Reads the Master Public IP ready for sending to the frontend
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
    network.destroy(username)
  else:
    print("Network doesn't exist")


#Obtain the OpenStack credentials from the environment
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
