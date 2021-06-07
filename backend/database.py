import argparse
import asyncio
import os
import sqlite3
import yaml

from aiohttp import web
from prettytable import PrettyTable

from constants import DATABASE_NAME

parser = argparse.ArgumentParser(description="Cluster Launcher User Manager - A system to view, edit and manage the user database associated with the Cluster Launcher.")
subparsers = parser.add_subparsers(dest='subparser')

#Parser for User interactions
parser_user = subparsers.add_parser('user', help="Manipulate a User in the User Table")
user_subparsers = parser_user.add_subparsers(dest='options')

#Add Users to the User Table
parser_add_user = user_subparsers.add_parser('add', help="Add a User in the User Table")
parser_add_user.add_argument('user', nargs=1, help="Username of the user to add")

#Remove Users from the User Table
parser_remove_user = user_subparsers.add_parser('remove', help="Remove a User in the User Table")
parser_remove_user.add_argument('user', nargs=1, help="Username of the user to add")

#Parser for the Volume Table
parser_volume = subparsers.add_parser('volume', help="Manipulate a Volume in the Volume Table")
volume_subparsers = parser_volume.add_subparsers(dest='options')

#Add Volume to Volume Table
parser_add_volume = volume_subparsers.add_parser('add')
parser_add_volume.add_argument('user', nargs=1)
parser_add_volume.add_argument('tenant_name', nargs=1)
parser_add_volume.add_argument('volume_name', nargs=1)
parser_add_volume.add_argument('-volSize', nargs=1)

#Remove Volume to Volume Table
parser_remove_volume = volume_subparsers.add_parser('remove')
parser_remove_volume.add_argument('user', nargs=1)
parser_remove_volume.add_argument('tenant_name', nargs=1)

#Parser for Tenant Interactions
parser_tenant = subparsers.add_parser('tenant', help="Manipulate a Tenant in the Tenant Table")
tenant_subparsers = parser_tenant.add_subparsers(dest='options')

#Populate the Tenant Table
parser_add_tenant = tenant_subparsers.add_parser('populate', help="Populate the Tenant's Table from tenants_conf.yml")
parser_remove_tenant = tenant_subparsers.add_parser('depopulate', help="Remove all rows in the Tenant's Table")

parser_search_tenant = tenant_subparsers.add_parser('search', help="Find a Tenant's ID")
parser_search_tenant.add_argument('tenant_name', nargs=1, help="Name of Tenant")

#Add users to the Tenant Table
parser_associate_user = subparsers.add_parser('link', help="Add a User to the Tenant's Database")
parser_associate_user.add_argument('user', nargs=1, help="Username of the user to add")
parser_associate_user.add_argument('tenant_name', nargs=1, help="Name of the tenant to add the user to")

#Remove users from the tenants database
parser_deassociate_user = subparsers.add_parser('delink', help="Remove a User from the Tenant's Database.")
parser_deassociate_user.add_argument('user', help="Username of the user to remove")
parser_deassociate_user.add_argument('tenant_name', help="Name of the tenant to remove the user from")

parser_cluster = subparsers.add_parser('cluster', help="Manage a Cluster in the database in the event of errors")
cluster_subparsers = parser_cluster.add_subparsers(dest='options')

parser_remove_cluster = cluster_subparsers.add_parser('remove', help="Remove a Cluster from the table")
parser_remove_cluster.add_argument('user', help="Username of the user to remove")
parser_remove_cluster.add_argument('tenant_name', help="Name of the tenant")

parser_network = subparsers.add_parser('network', help="Manage a Network in the database in the event of errors")
network_subparsers = parser_network.add_subparsers(dest='options')

parser_remove_network = network_subparsers.add_parser('remove', help="Remove a Network from the table")
parser_remove_network.add_argument('user', help="Username of the user to remove")
parser_remove_network.add_argument('tenant_name', help="Name of the tenant")



parser_search = subparsers.add_parser('search', help="Search to find a user-tenant mapping")
parser_search.add_argument('user', help="Username of the user to remove")
parser_search.add_argument('tenant_name', help="ID of the tenant to remove the user from")

#Parser for outputting information to users
parser_list = subparsers.add_parser('list', help="List information stored in tables")
list_subparsers = parser_list.add_subparsers(dest='options')
#Output tenant table information
parser_list_tenants = list_subparsers.add_parser('tenant')
#Output user table information
parser_list_users = list_subparsers.add_parser('user')
#Output mapping table information
parser_list_mappings = list_subparsers.add_parser('mapping')
#Output clusters table information
clusters_list_mappings = list_subparsers.add_parser('clusters')
#Output networks table information
networks_list_mappings = list_subparsers.add_parser('networks')
#Output volumes table information
volumes_list_mappings = list_subparsers.add_parser('volumes')

def initialise_database():
  #Initialise the database by creating the SQL tables if not present already
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  cursor.execute('''CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY NOT NULL)
  ''')

  cursor.execute('''CREATE TABLE IF NOT EXISTS tenants(
    tenants_name TEXT PRIMARY KEY NOT NULL,
    tenants_id TEXT NOT NULL,
    lustre_description TEXT NOT NULL)
  ''')

  cursor.execute('''CREATE TABLE IF NOT EXISTS user_tenant_mapping(
    username TEXT NOT NULL REFERENCES users(username),
    tenant_name TEXT NOT NULL REFERENCES tenants(tenants_name),
    PRIMARY KEY (username, tenant_name))
  ''')

  cursor.execute('''CREATE TABLE IF NOT EXISTS volumes(
    username TEXT NOT NULL REFERENCES users(username),
    tenant_name TEXT NOT NULL REFERENCES tenants(tenants_name),
    volume_name TEXT NOT NULL,
    volume_size INTEGER,
    PRIMARY KEY (username, tenant_name))
  ''')

  db.commit()

  return db, cursor


def add_user(user):
  db, cursor = initialise_database()

  try:
    cursor.execute("INSERT INTO users (username) VALUES (?)",(user))
    db.commit()
  except sqlite3.IntegrityError:
    print("Username is already registered in the Database")

  db.close()


def remove_user(user):
  db, cursor = initialise_database()

  cursor.execute("DELETE from users where username = ?", (user))

  db.commit()
  db.close()


def add_volume(user, tenant_name, volume_name):
  db, cursor = initialise_database()

  try:
    cursor.execute("INSERT INTO volumes (username, tenant_name, volume_name) VALUES (?,?,?)",(user,tenant_name,volume_name))
    db.commit()
  except sqlite3.IntegrityError:
    print("Username already has a volume registered to that tenant")

  db.close()


def remove_volume(user, tenant_name):
  db, cursor = initialise_database()

  cursor.execute("DELETE from volumes where username = ? AND tenant_name = ?", (user, tenant_name))

  db.commit()
  db.close()

def remove_cluster(user, tenant_name):
  db, cursor = initialise_database()

  cursor.execute("DELETE from clusters where username = ? AND tenant_name = ?", (user, tenant_name))

  db.commit()
  db.close()

def remove_network(user, tenant_name):
  db, cursor = initialise_database()

  cursor.execute("DELETE from networking where user_name = ? AND tenant_name = ?", (user, tenant_name))

  db.commit()
  db.close()

def populate_tenants():
  db, cursor = initialise_database()

  with open('tenants_conf.yml', 'r') as tenant_file:
    data = yaml.load(tenant_file, Loader=yaml.Loader)

  for tenant in data['tenants']:
    id = data['tenants'].get(tenant)
    lustre_desc = ""
    try:
      cursor.execute("INSERT INTO tenants (tenants_name, tenants_id, lustre_description) VALUES (?, ?, ?)",(tenant, id, lustre_desc))
      db.commit()
    except sqlite3.IntegrityError:
      pass

  db.close()


def depopulate_tenants():
  db, cursor = initialise_database()

  cursor.execute("DELETE FROM tenants")
  print(str(cursor.rowcount) + " rows have been deleted from the tenant table")
  db.commit()
  db.close()

def link_tables(user, tenant):
  db, cursor = initialise_database()

  cursor.execute('pragma foreign_keys=ON')

  tenant = tenant.lower()

  cursor.execute("INSERT INTO user_tenant_mapping (username, tenant_name) VALUES (?, ?)",(user, tenant))

  db.commit()
  db.close()

def delink_tables(user, tenant):
  db, cursor = initialise_database()

  tenant = tenant.lower()

  cursor.execute("DELETE from user_tenant_mapping where username = ? AND tenant_name = ?;", (user, tenant))

  db.commit()
  db.close()


def display_tenants():
  db, cursor = initialise_database()

  cursor.execute("SELECT * from tenants ORDER BY tenants_name")
  results = cursor.fetchall()

  table = PrettyTable()
  table.field_names = ["Tenant Name", "Tenant ID", "Lustre Description"]
  table.align["Tenant Name"] = "l"

  for tenant in results:
    row = [str(tenant[0]), str(tenant[1]), str(tenant[2])]
    table.add_row(row)

  print(table)

  db.close()

def display_users():
  db, cursor = initialise_database()

  cursor.execute("SELECT * from users ORDER BY username")
  results = cursor.fetchall()

  table = PrettyTable()
  table.field_names = ["Username"]

  for user in results:
    row = [str(user[0])]
    table.add_row(row)

  print(table)

  db.close()

def display_mapping():
  db, cursor = initialise_database()

  cursor.execute("SELECT * from user_tenant_mapping ORDER BY username")
  results = cursor.fetchall()

  table = PrettyTable()
  table.field_names = ["Username", "Tenant Name"]

  for mapping in results:
    row = [str(mapping[0]), str(mapping[1])]
    table.add_row(row)

  print(table)

  db.close()


def display_clusters():
  db, cursor = initialise_database()

  cursor.execute("SELECT * from clusters ORDER BY username")
  results = cursor.fetchall()

  table = PrettyTable()
  table.field_names = ["Username", "Tenant Name", "Cluster IP", "Number of Workers"]

  for clusters in results:
    row = [str(clusters[0]), str(clusters[1]), str(clusters[2]), str(clusters[3])]
    table.add_row(row)

  print(table)

  db.close()

def display_networks():
  db, cursor = initialise_database()

  cursor.execute("SELECT * from networking ORDER BY user_name")
  results = cursor.fetchall()

  table = PrettyTable()
  table.field_names = ["Username", "Network ID", "Subnet ID", "Router ID", "Tenant"]

  for networks in results:
    row = [str(networks[0]), str(networks[1]), str(networks[2]), str(networks[3]), str(networks[4])]
    table.add_row(row)

  print(table)

  db.close()

def display_volumes():
  db, cursor = initialise_database()

  cursor.execute("SELECT * from volumes ORDER BY username")
  results = cursor.fetchall()

  table = PrettyTable()
  table.field_names = ["Username", "Tenant Name", "Volume Name", "Volume Size"]

  for volumes in results:
    row = [str(volumes[0]), str(volumes[1]), str(volumes[2]), str(volumes[3])]
    table.add_row(row)

  print(table)

  db.close()


def request_mappings(request):
  db, cursor = initialise_database()

  cursor.execute("SELECT * from user_tenant_mapping ORDER BY username")
  results = cursor.fetchall()

  db.close()

  return web.json_response(results)

def search_user(user, tenant_name):
  db, cursor = initialise_database()

  cursor.execute("SELECT * from user_tenant_mapping WHERE username = ? AND tenant_name = ?",(user,tenant_name))
  result = cursor.fetchall()

  db.close()

  if result == []:
    return False
  else:
    return True

def fetch_id(tenant_name):
  db, cursor = initialise_database()

  cursor.execute("SELECT tenants_id from tenants WHERE tenants_name = ?", [tenant_name])
  tenant_id = cursor.fetchall()

  return tenant_id[0][0]


def checkVolumes(username, tenant_name):
  db, cursor = initialise_database()

  cursor.execute("SELECT volume_name from volumes WHERE username = ? AND tenant_name = ?", [username, tenant_name])
  try:
    volume_name = cursor.fetchall()[0][0]

  except Exception:
    volume_name = None

  return volume_name

def checkMappings(request):

  db, cursor = initialise_database()


  if 'X-Forwarded-User' in request.headers:
    username = request.headers['X-Forwarded-User']
  else:
    #For testing purposes
    username = "an12"

  cursor.execute("SELECT tenant_name from user_tenant_mapping WHERE username = ?", [username])
  list_of_tenant_names = cursor.fetchall()

  array = {}
  for tenant_name in list_of_tenant_names:
    volume_name = checkVolumes(username, tenant_name[0])

    array[tenant_name[0]] = volume_name

  return web.json_response(array)


if __name__ == '__main__':
  args = parser.parse_args()
  #Manage Users Table
  if args.subparser == "user":
    #Add a user to the user's table
    if args.options == "add":
      add_user(args.user)
    #Remove a user from the user's table
    if args.options == "remove":
      remove_user(args.user)

  if args.subparser == "volume":
    if args.options == "add":
      add_volume(args.user[0], args.tenant_name[0], args.volume_name[0])
    if args.options == "remove":
      remove_volume(args.user[0], args.tenant_name[0])

  if args.subparser == "cluster":
    if args.options == "remove":
      remove_cluster(args.user[0], args.tenant_name[0])

  if args.subparser == "network":
    if args.options == "remove":
      remove_network(args.user[0], args.tenant_name[0])

  #Populate the Tenant's Table
  if args.subparser == "tenant":
    if args.options == "populate":
      populate_tenants()
    if args.options == "depopulate":
      depopulate_tenants()
    if args.options == "search":
      fetch_id(args.tenant_name[0])

  #Add links in the User-Tenant Mapping Table
  if args.subparser == "link":
    link_tables(args.user[0], args.tenant_name[0])
  #Delink in the User-Tenant Mapping Table
  if args.subparser == "delink":
    delink_tables(args.user, args.tenant_name)
  #List the tenants currently stored
  if args.subparser == "list":
    if args.options == "tenant":
      display_tenants()
    if args.options == "user":
      display_users()
    if args.options == "mapping":
      display_mapping()
    if args.options == "clusters":
      display_clusters()
    if args.options == "networks":
      display_networks()
    if args.options == "volumes":
      display_volumes()

  if args.subparser == "search":
    search_user(args.user, args.tenant_name)
