from constants import DATABASE_NAME

import os
import sqlite3
from keystoneauth1 import identity, session

username = "an12"

def _neutron():
    creds = {
        "auth_url":          os.environ["OS_AUTH_URL"] + "/v3",
        "username":          os.environ["OS_USERNAME"],
        "password":          os.environ["OS_PASSWORD"],
        "project_name":      os.environ["OS_PROJECT_NAME"],
        "project_domain_id": "default",  # OS_PROJECT_DOMAIN_ID
        "user_domain_id":    "default"   # OS_USER_DOMAIN_NAME fails; case-dependent
    }

    #return client.Client(session=session.Session(auth=identity.Password(**creds)))

def initialise_database():
  #Initialise the database by creating the SQL tables if not present already
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  try:
    cursor.execute('''CREATE TABLE users(
      username TEXT PRIMARY KEY NOT NULL
    ''')

  except sqlite3.OperationalError:
    # this triggers when table "networking" already exists in the DB
    print("Database Already Initialised")
    pass
  try:
    cursor.execute('''CREATE TABLE tenants(
      tenants_id TEXT PRIMARY KEY NOT NULL,
      lustre_description TEXT NOT NULL
    ''')
  except sqlite3.OperationalError:
    # this triggers when table "networking" already exists in the DB
    print("Database Already Initialised")
    pass
  try:
    cursor.execute('''CREATE TABLE user_tenant_mapping(
       username TEXT NOT NULL REFERENCES users(username),
       tenant_id TEXT NOT NULL REFERENCES tenants(tenants_id),
       PRIMARY KEY (username, tenant_id)
    ''')
  except sqlite3.OperationalError:
    # this triggers when table "networking" already exists in the DB
    print("Database Already Initialised")
    pass
  print("THIS IS REACHING TENANTS.PY")
  db.commit()
  db.close()


initialise_database()
