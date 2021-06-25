import os
from unittest import TestCase
from unittest.mock import Mock, patch
from backend import network
import neutronclient.v2_0

class TestNetworking(TestCase):
    @patch.dict(os.environ, {"OS_AUTH_URL": "auth/path", "OS_USERNAME":"test-user","OS_PASSWORD":"test-password"})
    def test_credentials(self):
        creds = network._neutron('test-tenant')
        self.assertIsInstance(creds, neutronclient.v2_0.client.Client)


'''
    #This is currently not testing anything
    #This needs to be turned into integration testing (actually testing the network comes up)
    @patch('network.database')
    def test_create(self, mocked_db):
        connection = Mock()
        #Create Dummy Networks
        network1, network2 = DummyNetwork("test-network1", "1"), DummyNetwork("test-network2", "2")
        #Mock a list of networks
        connection.network.networks.return_value = [network1, network2]
        mocked_db.initialise_database.return_value = mocked_db, "Cursor"
        
        
        network.create(connection, 'test-user', 'test-tenant')


class DummyNetwork():
    def __init__(self, name, id):
        self.name = name
        self.id = id

class DummyDatabase():
    def __init__(self):
        pass
    def close(self):
        pass
'''