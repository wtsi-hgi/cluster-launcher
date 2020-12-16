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



'''    path = "../clusters/" + user
    if (os.path.isdir(path)):
        #If cluster file for user exists, do something
        pass
    else:
        subprocess.Popen(['bash', 'user-creation.sh', path])
        #os.mkdir(path)
        #os.mkdir(path + "terraform")


if __name__ == "__main__":
    username="an12"
    num_workers="2"
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSIYcwRdIM5Ny4I6613oSWsyQtnurMqwzMDFUxpz6fLPbg7+MoEfmetLoMgMywayS6rSF+GkFoG6zPMJoV0EnDlLwmWGjvCkwywtVo93mjtwkfdvEqgw5FOBG+UNumlwZI/kLLUSh9rD+5wIZXAWHRJ9n42XuQWDvadB4IOLlpS8M2YQVHnwcDQLb3fV4nBLpHOXuFQA6wNnwQjI1Fk5OXtmLPl9PkX5GGX3C9sPC81SDlO/gmtvWE33zF2/DYamAFU4BXOdrT3S6vHpmb7ihTwWu634BHPWA6iEPis3LOVsbzw9TC6RjMUomlvPWBkglovEXEf9RXIExF+wTi4XiB an12@mib114726i"
    flavor="m1.small"
    image_name="bionic-WTSI-docker_49930_38ab07e9"
    vol_name="NA"
    vol_size="1"
    device_name="NA"

    #1. Read username from cookie
    #2. Check if user already has a cluster
    #3a If yes, launch Jupter Notebook
    #3b. If no, let user create cluster
    startup(username, num_workers, public_key, flavor, image_name, vol_name, vol_size, device_name)
'''
