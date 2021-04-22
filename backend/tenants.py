#from constants import DATABASE_NAME
DATABASE_NAME = "../../clusters/cluster-networking.db"
import argparse
import os
import sqlite3
import yaml

from prettytable import PrettyTable


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

#Parser for Tenant Interactions
parser_tenant = subparsers.add_parser('tenant', help="Manipulate a Tenant in the Tenant Table")
tenant_subparsers = parser_tenant.add_subparsers(dest='options')

#Populate the Tenant Table
parser_add_tenant = tenant_subparsers.add_parser('populate', help="Populate the Tenant's Table from tenants_conf.yml")
parser_remove_tenant = tenant_subparsers.add_parser('depopulate', help="Remove all rows in the Tenant's Table")

#Add users to the Tenant Table
parser_associate_user = subparsers.add_parser('link', help="Add a User to the Tenant's Database")
parser_associate_user.add_argument('user', nargs=1, help="Username of the user to add")
parser_associate_user.add_argument('tenant_id', nargs=1, help="ID of the tenant to add the user to")

#Remove users from the tenants database
parser_deassociate_user = subparsers.add_parser('delink', help="Remove a User from the Tenant's Database.")
parser_deassociate_user.add_argument('user', help="Username of the user to remove")
parser_deassociate_user.add_argument('tenant_id', help="ID of the tenant to remove the user from")

#Parser for outputting information to users
parser_list = subparsers.add_parser('list', help="List information stored in tables")
list_subparsers = parser_list.add_subparsers(dest='options')
#Output tenant table information
parser_list_tenants = list_subparsers.add_parser('tenant')
#Output user table information
parser_list_users = list_subparsers.add_parser('user')
#Output mapping table information
parser_list_mappings = list_subparsers.add_parser('mapping')

def initialise_database():
  #Initialise the database by creating the SQL tables if not present already
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  cursor.execute('''CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY NOT NULL)
  ''')

  cursor.execute('''CREATE TABLE IF NOT EXISTS tenants(
    tenants_id TEXT PRIMARY KEY NOT NULL,
    tenants_name TEXT NOT NULL,
    lustre_description TEXT NOT NULL)
  ''')

  cursor.execute('''CREATE TABLE IF NOT EXISTS user_tenant_mapping(
    username TEXT NOT NULL REFERENCES users(username),
    tenant_id TEXT NOT NULL REFERENCES tenants(tenants_id),
    PRIMARY KEY (username, tenant_id))
  ''')

  db.commit()
  db.close()


def add_user(user):
  initialise_database()
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()
  try:
    cursor.execute("INSERT INTO users (username) VALUES (?)",(user))
  except sqlite3.IntegrityError:
    print("Username is already registered in the Database")
  db.commit()
  db.close()


def remove_user(user):
  initialise_database()
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  cursor.execute("DELETE from users where username = ?", (user))

  db.commit()
  db.close()


def populate_tenants():
  initialise_database()
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  with open('tenants_conf.yml', 'r') as tenant_file:
    data = yaml.load(tenant_file, Loader=yaml.Loader)

  for tenant in data['tenants']:
    id = data['tenants'].get(tenant)
    lustre_desc = ""
    try:
      cursor.execute("INSERT INTO tenants (tenants_id, tenants_name, lustre_description) VALUES (?, ?, ?)",(id, tenant, lustre_desc))
    except sqlite3.IntegrityError:
      pass

  db.commit()
  db.close()


def depopulate_tenants():
  initialise_database()
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  cursor.execute("DELETE FROM tenants")
  print(str(cursor.rowcount) + " rows have been deleted from the tenant table")
  db.commit()
  db.close()

def link_tables(user, tenant):
  initialise_database()
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  cursor.execute('pragma foreign_keys=ON')

  cursor.execute("INSERT INTO user_tenant_mapping (username, tenant_id) VALUES (?, ?)",(user, tenant))

  db.commit()
  db.close()

def delink_tables(user, tenant):
  initialise_database()
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  cursor.execute("DELETE from user_tenant_mapping where username = ? AND tenant_id = ?;", (user, tenant))

  db.commit()
  db.close()


def display_tenants():
  initialise_database()
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  cursor.execute("SELECT * from tenants")
  results = cursor.fetchall()

  table = PrettyTable()
  table.field_names = ["Tenant Name", "Tenant ID", "Lustre Description"]
  table.align["Tenant Name"] = "l"

  for tenant in results:
    row = [str(tenant[1]), str(tenant[0]), str(tenant[2])]
    table.add_row(row)

  print(table)


def display_users():
  initialise_database()
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  cursor.execute("SELECT * from users")
  results = cursor.fetchall()

  table = PrettyTable()
  table.field_names = ["Username"]

  for user in results:
    row = [str(user[0])]
    table.add_row(row)

  print(table)

def display_mapping():
  initialise_database()
  db = sqlite3.connect(DATABASE_NAME)
  cursor = db.cursor()

  cursor.execute("SELECT * from user_tenant_mapping")
  results = cursor.fetchall()

  table = PrettyTable()
  table.field_names = ["Username", "Tenant ID"]

  for mapping in results:
    row = [str(mapping[0]), str(mapping[1])]
    table.add_row(row)

  print(table)



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

  #Populate the Tenant's Table
  if args.subparser == "tenant":
    if args.options == "populate":
      populate_tenants()
    if args.options == "depopulate":
      depopulate_tenants()

  #Add links in the User-Tenant Mapping Table
  if args.subparser == "link":
    link_tables(args.user[0], args.tenant_id[0])

  #Delink in the User-Tenant Mapping Table
  if args.subparser == "delink":
    delink_tables(args.user[0], args.tenant_id[0])

  #List the tenants currently stored
  if args.subparser == "list":
    if args.options == "tenant":
      display_tenants()
    if args.options == "user":
      display_users()
    if args.options == "mapping":
      display_mapping()
