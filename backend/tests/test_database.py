import tempfile
import os
import sqlite3
import subprocess
from unittest import mock

from unittest.mock import Mock, patch
from unittest import TestCase

import database
from constants import TEST_PATH

class TestDatabase(TestCase):
  def setUp(self) -> None:
    database.DATABASE_NAME = TEST_PATH

  def tearDown(self) -> None:
    database.DATABASE_NAME = '/backend/clusters/cluster-networking.db'
    try:
      os.remove(TEST_PATH)
    except Exception:
      pass
  
  def test_database_file(self):
    #This functionality will only pass a test when the test is ran from within a container
    file_path = "/backend/clusters/cluster-networking.db"
    if os.path.isdir('/backend'):
      isFile = os.path.isfile(file_path)
      self.assertEqual(isFile, True)

  def test_users(self):
    database.add_user(['test-user'])
    result = check_database_entry_value(database.DATABASE_NAME, "username", "users", 'test-user')
    #Confirms User is added to the database
    self.assertIn('test-user', result[0])
    #Removes User from database
    database.remove_user(['test-user'])
    result = check_database_entry_value(database.DATABASE_NAME, "username", "users", 'test-user')
    self.assertEqual(result, [])

  def test_tenants(self):
    #Initialise db and cursor to use throughout test
    db = sqlite3.connect(database.DATABASE_NAME)
    cursor = db.cursor()
    #Populate the database with the tenants config
    database.populate_tenants()
    #Grab resulting tenants table
    result = check_database_entry(database.DATABASE_NAME, "tenants_name", "tenants")
    #result is in the form of a list of tuples, this for loop strips this into a list of strings
    untupled_result = []
    for tenant_name in result:
      untupled_result.append(tenant_name[0])
    #Test if HGI is in the table
    self.assertIn('hgi', untupled_result)
    #Test that there is a successful delete of all tenants
    cursor.execute("DELETE FROM tenants")
    self.assertEqual(cursor.rowcount, 8)
    db.commit() 
    empty_result = check_database_entry(database.DATABASE_NAME, "tenants_name", "tenants")
    self.assertEqual(empty_result, [])
    db.close()

  def test_mappings(self):
    db, cursor = database.initialise_database()
    cursor.execute("INSERT INTO users (username) VALUES (?)", ['test-user'])
    cursor.execute("INSERT INTO tenants (tenants_name, tenants_id, lustre_description) VALUES (?, ?, ?)",('test-tenant', 'test-tenant-id', 'NA'))
    db.commit()
    database.link_tables('test-user', 'test-tenant')
    linked_results = check_database_entry(database.DATABASE_NAME, 'username, tenant_name','user_tenant_mapping')
    self.assertIsNot(linked_results, [])
    self.assertIn('test-user', linked_results[0])
    self.assertIn('test-tenant', linked_results[0])
    database.delink_tables('test-user', 'test-tenant')
    empty_linked_results = check_database_entry(database.DATABASE_NAME, 'username, tenant_name','user_tenant_mapping')
    self.assertEqual(empty_linked_results, [])
    self.assertNotIn('test-user', empty_linked_results)
    self.assertNotIn('test-tenant', empty_linked_results)

  def test_volumes(self):
    db, cursor = database.initialise_database()
    cursor.execute("INSERT INTO users (username) VALUES (?)", ['test-user'])
    cursor.execute("INSERT INTO tenants (tenants_name, tenants_id, lustre_description) VALUES (?, ?, ?)",('test-tenant', 'test-tenant-id', 'NA'))
    db.commit()
    database.add_volume('test-user', 'test-tenant', 'test-volume')
    volume_result = check_database_entry_value(database.DATABASE_NAME, 'volume_name', 'volumes', 'test-volume')
    self.assertEqual(volume_result[0][0], 'test-volume')
    self.assertTupleEqual(volume_result[0], ('test-volume',))
    self.assertNotEqual(volume_result[0][0], 'failed-test-volume')
    database.remove_volume('test-user', 'test-tenant')
    empty_volume_table = check_database_entry(database.DATABASE_NAME, '*', 'volumes')
    self.assertEqual(empty_volume_table, [])

  def test_clusters(self):
    db, cursor = database.initialise_database()
    database.add_cluster('test-user', 'test-tenant', 'test-cluster-ip', 'test-workers-num')
    cluster_result = check_database_entry(database.DATABASE_NAME, '*', 'clusters')
    self.assertEqual(cluster_result, [('test-user', 'test-tenant', 'test-cluster-ip', 'test-workers-num',)])
    cluster_ip_result = check_database_entry_value(database.DATABASE_NAME, 'cluster_ip', 'clusters', 'test-cluster-ip')
    self.assertEqual(cluster_ip_result, [('test-cluster-ip',)])
    cursor.execute("SELECT cluster_ip FROM clusters WHERE username = 'test-user'")
    cluster_ip_result2 = cursor.fetchall()
    self.assertEqual(cluster_ip_result2, [('test-cluster-ip',)])
    database.remove_cluster('test-user')
    empty_cluster_table = check_database_entry(database.DATABASE_NAME, '*', 'clusters')
    self.assertEqual(empty_cluster_table, [])


  def test_networks(self):
    db, cursor = database.initialise_database()
    database.add_network('test-user', 'test-network-id', 'test-subnet-id', 'test-router-id', 'test-tenant')
    test_network_entry = check_database_entry(database.DATABASE_NAME, '*', 'networking')
    self.assertEqual(test_network_entry, [('test-user', 'test-network-id', 'test-subnet-id', 'test-router-id', 'test-tenant')])
    database.remove_network('test-user', 'test-tenant')
    test_network_empty = check_database_entry(database.DATABASE_NAME, '*', 'networking')
    self.assertEqual(test_network_empty, [])


def check_database_entry(temp_file, option, table):
  db = sqlite3.connect(temp_file)
  cursor = db.cursor()
  query = "SELECT " + option + " FROM " + table
  cursor.execute(query)
  return(cursor.fetchall())

def check_database_entry_value(temp_file, option, table, field):
  db = sqlite3.connect(temp_file)
  cursor = db.cursor()
  query = "SELECT " + option + " FROM " + table + " WHERE " + option + " = '" + field+"'"
  cursor.execute(query)
  return(cursor.fetchall())