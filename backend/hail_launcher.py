import json
import subprocess
import time

import asyncio
import openstack
import os
import sqlite3
import yaml
from aiohttp import web
from concurrent.futures import ThreadPoolExecutor
from os import path

import network
import database
from constants import DATABASE_NAME

DEBUG = False

async def startup(request):

  if 'X-Forwarded-User' in request.headers:
    username = request.headers['X-Forwarded-User']
  else:
    #For testing purposes
    username = "an12"

  #Request returned from the frontend is in the form:
  #The Request will either specify volSize or the volume_name, not both
  # {
  #   public_key: String,
  #   workers: String,
  #   password: String,
  #   flavor: String,
  #   tenant: String,
  #   status: Boolean,
  #   volSize: Integer - Not Required,
  #   volume_name: String - Not Required
  # }
  attributes = await request.json()

  #Initialise the Pool and Jobs dictionary as variables
  jobs = request.app["jobs"]
  pool = request.app["pool"]

  tenant_verification = database.search_user(username, attributes['tenant'])

  if tenant_verification == False:
    return web.Response(text="Unverified User")
  else:
    #Creates a thread with cluster creation code to prevent blocking the handler
    jobs[username] = ( pool.submit(cluster_creator, request, attributes, username), "UP" )
    if DEBUG:
      jobs[username][0].result()

    return web.Response(text="Verified User")


def cluster_creator(request, attributes, username):
  #Attributes passed in the form:
  # {
  #   public_key: String,
  #   workers: String,
  #   password: String,
  #   flavor: String,
  #   status: Boolean
  #   volSize: Integer - Not Required,
  #   volume_name: String - Not Required
  # }

#  with open('public_key.pub', 'w') as key_file:
#    key_file.write(attributes["public_key"])

  credentials = get_credentials(attributes['tenant'])
  conn = openstack.connect(**credentials)
  osdataproc_creds = env_credentials(attributes['tenant'])

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
      create_network(conn, username, attributes['tenant'])
      #Run the cluster creation bash script
      if "volume_name" in attributes:
        #Volume Size is set to zero if volume exists for the user in the tenant
        volume_size = '0'
        print("Username: " + username + " is creating a cluster in " + attributes['tenant'] +", using volume: " + attributes['volume_name'])
        process = subprocess.run(['bash', 'cluster-creation.sh', username, attributes["password"],
                                 attributes["workers"], attributes["flavor"], attributes["volume_name"],
                                 volume_size], env = osdataproc_creds, capture_output=True, text=True)
      else:
        #If the user does not have a volume in the tenant, one is created for them
        #in the schema of USERNAME-cluster-volume
        volume_name = username+'-cluster-volume'
        database.add_volume(username, attributes['tenant'], volume_name)
        print("Creating Volume called: " + volume_name + " of size: " + attributes["volSize"])
        print("Username: " + username + " is creating a cluster in " + attributes['tenant'] +", using volume: " + volume_name)
        process = subprocess.run(['bash', 'cluster-creation.sh', username, attributes["password"],
                                 attributes["workers"], attributes["flavor"], volume_name, attributes["volSize"]],
                                 env = osdataproc_creds, capture_output=True, text=True)
      if DEBUG:
        print(process)

      try:
        path_to_cluster_ip = '/backend/clusters/' + username + '/osdataproc/terraform/terraform.tfstate.d/' + username + '/outputs.json'

        if path.exists(path_to_cluster_ip):
          with open(path_to_cluster_ip) as json_file:
            data = json.load(json_file)
            cluster_ip = data["spark_master_public_ip"]["value"]
          add_cluster(username, attributes['tenant'], cluster_ip, attributes['workers'])
          user_key_path = "/backend/clusters/"+username+"/pubkey.pub"
          cluster_location = "ubuntu@"+cluster_ip
          print(user_key_path)
          print(attributes["public_key"])
          with open(user_key_path, 'w') as key_file:
            key_file.write(attributes["public_key"])


          subprocess.run(['ssh-copy-id', '-f', '-i', user_key_path, cluster_location], capture_output=True, text=True)
      except:
        print("Error has occured when registering this cluster")


async def tear_down(request):
  #Request returned from the frontend is in the form:
  # {
  #   status: Boolean
  # }
  attributes = await request.json()

  if 'X-Forwarded-User' in request.headers:
    username = request.headers['X-Forwarded-User']
  else:
    #For testing purposes
    username = "an12"

  #Initialise the Pool and Jobs dictionary as variables
  jobs = request.app["jobs"]
  pool = request.app["pool"]

  #Start a Thread with cluster deletion code to prevent blocking the handler
  jobs[username] = ( pool.submit(cluster_deletion, request, attributes, username), "DOWN" )
  if DEBUG:
    jobs[username][0].result()

  return web.Response(text="Cluster Deletion in Progress")


def cluster_deletion(request, attributes, username):
  tenant_name = tenant_finder(username)

  #Take OpenStack credentials from the OS_* environment variables and create a connection object
  credentials = get_credentials(tenant_name)
  conn = openstack.connect(**credentials)

  osdataproc_creds = env_credentials(tenant_name)

  if attributes["status"] == True:
    if path.exists('/backend/clusters/'+username):
      #Job Tuple for destroying clusters. Useful for checking status of jobs and their state
      process = subprocess.run(['bash', 'cluster-deletion.sh', username], env= osdataproc_creds, capture_output=True, text=True)
      if DEBUG:
        print(process)
      destroy_network(conn, username, tenant_name)
      remove_cluster(username)

    else:
      #Improve Logging for Error Messages
      #This error is called if there is no cluster to delete but the backend believes it exists
      print("No cluster exists - an error has occured")



async def job_status(request):
  #Assign the Jobs Dictionary to the variable jobs
  jobs = request.app["jobs"]

  if 'X-Forwarded-User' in request.headers:
    username = request.headers['X-Forwarded-User']
  else:
    #For testing purposes
    username = "an12"


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


def create_network(conn, username, tenant_name):
  network_name = username+"-cluster-network"
  network_list = [network.name for network in conn.network.networks()]

  if network_name in network_list:
    print(username + "'s network failed to destroy last session. Using: " + network_name + "again!")
  else:
    network.create(username, tenant_name)


def destroy_network(conn, username, tenant_name):
  prefix = username+"-cluster"
  network_name = prefix + "-network"

  network_list = [network.name for network in conn.network.networks()]

  if network_name in network_list:
    network.destroy(username, tenant_name)
  else:
    print("Error: Failed to destroy network: " + network_name + "as the network does not exist.")


#Obtain the OpenStack credentials from the environment
def get_credentials(tenant_name):
  d = {}
  try:
    tenant_id = database.fetch_id(tenant_name)
    d['version']  = "2"
    d['username'] = os.environ['OS_USERNAME']
    d['api_key'] = os.environ['OS_PASSWORD']
    d['auth_url'] = os.environ['OS_AUTH_URL']
    d['project_id'] = tenant_id
  except KeyError:
    raise Exception("Could not find all required fields in the environment")

  return d

def env_credentials(tenant_name):
  creds = {**os.environ}
  try:
    tenant_id = database.fetch_id(tenant_name)
    creds['OS_AUTH_URL'] = os.environ['OS_AUTH_URL']
    creds['OS_IDENTITY_API_VERSION'] = os.environ['OS_IDENTITY_API_VERSION']
    creds['OS_USER_DOMAIN_NAME'] = os.environ['OS_USER_DOMAIN_NAME']
    creds['OS_PROJECT_DOMAIN_ID'] = os.environ['OS_PROJECT_DOMAIN_ID']
    creds['OS_USERNAME'] = os.environ['OS_USERNAME']
    creds['OS_PASSWORD'] = os.environ['OS_PASSWORD']
    creds['OS_REGION_NAME'] = os.environ['OS_REGION_NAME']
    creds['OS_INTERFACE'] = os.environ['OS_INTERFACE']
    creds['OS_PROJECT_ID'] = tenant_id
    creds['OS_PROJECT_NAME'] = tenant_name
  except KeyError:
    raise Exception("Could not find all required fields in the environment")

  return creds


async def get_flavors(request):
  tenant_name = await request.json()
  credentials = get_credentials(tenant_name['tenant'])
  conn = openstack.connect(**credentials)
  flavors=conn.list_flavors()
  flavor_list = {}
  accepted_prefix = ['m2', 's2']
  accepted_sizing = ['medium', 'large', 'xlarge', '2xlarge', '3xlarge', '4xlarge']
  for flavor in flavors:
    flavor_prefix = flavor.name[:2]
    flavor_suffix = flavor.name[3:]
    if flavor_prefix in accepted_prefix:
      if flavor_suffix in accepted_sizing:
        flavor_list[flavor.name] = flavor.name
  return web.json_response(flavor_list)


def initialise_cluster_table():
  #Initialise the database by creating the SQL tables if not present already
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  cursor.execute('''CREATE TABLE IF NOT EXISTS clusters(
                      username TEXT PRIMARY KEY NOT NULL,
                      tenant TEXT NOT NULL,
                      cluster_ip TEXT NOT NULL,
                      num_workers TEXT NOT NULL)
                ''')

  db.commit()
  db.close()

def tenant_finder(user):
  initialise_cluster_table()
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  cursor.execute('''SELECT tenant FROM clusters WHERE username = ?''',
                    (user,))
  tenant = cursor.fetchall()
  return tenant[0][0]

def remove_cluster(user):
  initialise_cluster_table()

  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  cursor.execute('''DELETE from clusters WHERE username = ?''', (user,))

  db.commit()
  db.close()


def add_cluster(user, tenant_name, cluster_ip, num_workers):
  initialise_cluster_table()

  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  try:
    cursor.execute('''INSERT INTO clusters (username, tenant, cluster_ip, num_workers)
                      VALUES (?, ?, ?, ?)''', (user, tenant_name, cluster_ip, num_workers))
  except sqlite3.IntegrityError:
    print("This user already has a cluster registered. An error has occured")

  db.commit()
  db.close()
