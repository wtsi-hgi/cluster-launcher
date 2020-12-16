from constants import DATABASE_NAME

import os
import sqlite3
from keystoneauth1 import identity, session
from neutronclient.v2_0 import client

def _neutron():
    creds = {
        "auth_url":          os.environ["OS_AUTH_URL"] + "/v3",
        "username":          os.environ["OS_USERNAME"],
        "password":          os.environ["OS_PASSWORD"],
        "project_name":      os.environ["OS_PROJECT_NAME"],
        "project_domain_id": "default",  # OS_PROJECT_DOMAIN_ID
        "user_domain_id":    "default"   # OS_USER_DOMAIN_NAME fails; case-dependent
    }

    return client.Client(session=session.Session(auth=identity.Password(**creds)))

def initialise_database():
  #Initialise the database by creating the SQL tables if not present already
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  try:
    cursor.execute('''CREATE TABLE networking(user_name TEXT PRIMARY KEY,
      network_id TEXT,
      subnet_id TEXT,
      router_id TEXT,
      cluster_ip TEXT)
    ''')
  except sqlite3.OperationalError:
    # this triggers when table "networking" already exists in the DB
    pass

  db.commit()
  db.close()

def create(username):
  prefix = username+"-cluster"
  neutron = _neutron()
  initialise_database()
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
    networking(user_name, network_id, subnet_id, router_id, cluster_ip)
    VALUES(?, ?, ?, ?, "Undefined")''',
    (username, network["id"], subnet["id"], router["id"]))

  db.commit()
  db.close()

def destroy(username):
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  neutron = _neutron()
  prefix = username+"-cluter"
  network_name = prefix+"-network"

  # Get the externally routed network
  cursor.execute('''SELECT * FROM networking WHERE user_name = ?''',(username,))
  search = cursor.fetchall()[0]
  network_id = search[1]
  subnet_id = search[2]
  router_id = search[3]

  neutron.remove_interface_router(router_id, {
    "subnet_id": subnet_id
  })

  neutron.delete_router(router_id)
  neutron.delete_subnet(subnet_id)
  neutron.delete_network(network_id)

  cursor.execute('''DELETE FROM networking WHERE user_name= ?''',(username,))
  print("Network deconstructed")
  db.commit()
  db.close()

