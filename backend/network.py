import os
import sqlite3
from keystoneauth1 import identity, session
from neutronclient.v2_0 import client

import database
from constants import DATABASE_NAME

#Credentials to log into the neutronclient
def _neutron(tenant_name):
  creds = {
    "auth_url":          os.environ["OS_AUTH_URL"] + "/v3",
    "username":          os.environ["OS_USERNAME"],
    "password":          os.environ["OS_PASSWORD"],
    "project_name":      tenant_name,
    "project_domain_id": "default",  # OS_PROJECT_DOMAIN_ID
    "user_domain_id":    "default"   # OS_USER_DOMAIN_NAME fails; case-dependent
  }
  #Returns a working logged in session
  return client.Client(session=session.Session(auth=identity.Password(**creds)))

# Due to IP Limitations, each cluster is created with its own network to allow the maximum
# number of worker nodes to be created per user. This function will assume that no
# existing network exists, pertaining to checks in hail_launcher.py
def create(conn, username, tenant_name):
  prefix = username+"-cluster"
  network_name = prefix+"-network"
  network_list = [network.name for network in conn.network.networks()]

  if network_name in network_list:
    print(username + "'s network failed to destroy last session. Using: " + network_name + " again!")
  else:

    neutron = _neutron(tenant_name)
    db, cursor = database.initialise_database()
    db.close()
    # Get the externally routed network
    public = neutron.list_networks(retrieve_all=True, **{
      "router:external": True
    })["networks"][0]

    # Create router with an external gateway to the public network
    router = neutron.create_router({"router": {
        "name":           f"{prefix}-router",
        "admin_state_up": True,
        "external_gateway_info": {
          "network_id": public["id"]
        }
    }})["router"]

    # Create network and subnet
    network = neutron.create_network({"network": {
        "name":           f"{prefix}-network",
        "admin_state_up": True
    }})["network"]

    subnet = neutron.create_subnet({"subnets": [{
        "name":       f"{prefix}-subnet",
        "network_id": network["id"],
        "ip_version": 4,
        "cidr":       "10.1.0.1/24"
    }]})["subnets"][0]

    # Attach router to subnet through interface
    interface = neutron.add_interface_router(router["id"], {
        "subnet_id": subnet["id"]
    })

    database.add_network(username, network["id"], subnet["id"], router["id"], tenant_name)

# This function will assume that no existing network exists, pertaining to
# checks in hail_launcher.py
def destroy(conn, username, tenant_name):
  prefix = username+"-cluster"
  network_name = username + "-cluster-network"
  network_list = [network.name for network in conn.network.networks()]

  if network_name in network_list:
    db, cursor = database.initialise_database()
    neutron = _neutron(tenant_name)

    try:
    # Get the externally routed network
      cursor.execute('''
        SELECT network_id, subnet_id, router_id
        FROM networking
        WHERE user_name = ? AND tenant_name = ?
      ''',(username, tenant_name))

      network_id, subnet_id, router_id = cursor.fetchone()

      db.close()

      neutron.remove_interface_router(router_id, {
        "subnet_id": subnet_id
      })

      neutron.delete_router(router_id)
      neutron.delete_subnet(subnet_id)
      neutron.delete_network(network_id)
    except Exception:
      print("Breaking on network removal")
    try:
      database.remove_network(username, tenant_name)
    except Exception:
      pass
  else:
    print("Error: Failed to destroy network: " + network_name + "as the network does not exist.")
