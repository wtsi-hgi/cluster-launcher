import tempfile
import os
import sqlite3
import subprocess
from unittest import mock

from unittest.mock import Mock, patch
from unittest import TestCase

import database


class TestDatabase(TestCase):
  '''
  def test_database_file(self):
    #db, cursor = database.initialise_database()
    file_path = "/home/ubuntu/backend/clusters/cluster-networking.db"
    isFile = os.path.isfile(file_path)
    self.assertEqual(isFile, True)
  '''

  @patch(database.DATABASE_NAME)
  def test_suite(self, mocked_db):
    def test_users(self, mocked_db):

      with tempfile.NamedTemporaryFile() as tempFile:
        mocked_db = tempFile.name
        database.add_user('test-user')
        result = check_database_entry(mocked_db, "username", "users")
        print(result)
        self.assertEqual()
  
    def test_tenants(self, mocked_db):
      db, cursor = database.initialise_database()
      with tempfile.NamedTemporaryFile() as tempFile:
        database.populate_tenants()
        result = check_database_entry(mocked_db, "tenants", "hgi")
        self.assertIn('hgi', result)
        cursor.execute("DELETE FROM tenants")
        self.assertEqual(cursor.rowcount, 8)
        db.commit()
        db.close()

    def test_mappings(self, mocked_db):
      with tempfile.NamedTemporaryFile() as tempFile:
        mocked_db = tempFile.name
        db, cursor = database.initialise_database()
        cursor.execute("INSERT INTO users (username) VALUES (?)",('test-user'))
        cursor.execute("INSERT INTO tenants (tenants_name, tenants_id, lustre_description) VALUES (?, ?, ?)",('test-tenant', 'test-tenant-id', 'NA'))
        db.commit()
        db.close()
        database.link_tables('test-user', 'test-tenant')


def check_database_entry(temp_file, option, table):
  db = sqlite3.connect(temp_file)
  cursor = db.cursor()
  query = "SELECT" + option + "FROM" + table
  cursor.execute(query)
  return(cursor.fetchall())