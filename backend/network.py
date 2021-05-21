from constants import DATABASE_NAME

import os
import sqlite3
from keystoneauth1 import identity, session
from neutronclient.v2_0 import client


def _neutron(tenant_name):
  creds = {
    "auth_url":          os.environ["OS_AUTH_URL"] + "/v3",
    "username":          os.environ["OS_USERNAME"],
    "password":          os.environ["OS_PASSWORD"],
    "project_name":      tenant_name,
    "project_domain_id": "default",  # OS_PROJECT_DOMAIN_ID
    "user_domain_id":    "default"   # OS_USER_DOMAIN_NAME fails; case-dependent
  }

  return client.Client(session=session.Session(auth=identity.Password(**creds)))

def initialise_database(username, tenant_name):
  #Initialise the database by creating the SQL tables if not present already
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  cursor.execute('''
    CREATE TABLE IF NOT EXISTS networking(
      user_name TEXT NOT NULL,
      network_id TEXT NOT NULL,
      subnet_id TEXT NOT NULL,
      router_id TEXT NOT NULL,
      tenant_name TEXT NOT NULL,
      PRIMARY KEY (user_name, tenant_name)
    )
  ''')

  cursor.execute('''SELECT * FROM networking WHERE user_name = ? AND tenant_name = ?''',(username, tenant_name,))

  db.commit()
  db.close()

# Due to IP Limitations, each cluster is created with its own network to allow the maximum
# number of worker nodes to be created per user. This function will assume that no
# existing network exists, pertaining to checks in hail_launcher.py
def create(username, tenant_name):
  prefix = username+"-cluster"
  neutron = _neutron(tenant_name)
  initialise_database(username, tenant_name)

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

  #Log IDs in a database
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  cursor.execute('''INSERT INTO
    networking(user_name, network_id, subnet_id, router_id, tenant_name)
    VALUES(?, ?, ?, ?, ?)''',
    (username, network["id"], subnet["id"], router["id"], tenant_name))

  db.commit()
  db.close()

# This function will assume that no existing network exists, pertaining to
# checks in hail_launcher.py
def destroy(username, tenant_name):
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()
  initialise_database(username, tenant_name)

  neutron = _neutron(tenant_name)

  try:
  # Get the externally routed network
    cursor.execute('''
      SELECT network_id, subnet_id, router_id
      FROM networking
      WHERE user_name = ? AND tenant_name = ?
    ''',(username, tenant_name))

    network_id, subnet_id, router_id = cursor.fetchone()

    neutron.remove_interface_router(router_id, {
      "subnet_id": subnet_id
    })

    neutron.delete_router(router_id)
    neutron.delete_subnet(subnet_id)
    neutron.delete_network(network_id)

    cursor.execute('''DELETE FROM networking WHERE user_name= ? AND tenant_name = ?''',(username, tenant_name))

  except sqlite3.OperationalError:
    # this triggers when table "networking" already exists in the DB
    print("An error has occured while deleting the network")
    pass
  except IndexError:
    print("Database is empty and therefore cannot delete network")
    pass
  db.commit()
  db.close()
