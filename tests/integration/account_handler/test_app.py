from unittest import TestCase
import os
import requests

# TODO clean up created resources from testing
class TestApiGateway(TestCase):

    def setUp(self):


        self.api_endpoint = 'https://v33bcr3lbl.execute-api.eu-west-1.amazonaws.com/Prod'
        #self.api_endpoint = os.environ['api-endpoint']
        #self.api_endpoint = 'http://127.0.0.1:3000/account/Prod'

        self.event = {"username": "test5@email.com", "password": "password"}

    def test_api_gateway(self):
        headers = headers = {'Content-type': 'application/json', 'Accept':'application/json'}
        
        actual_result = requests.post(self.api_endpoint, json=self.event, headers=headers)

        with self.subTest():
            self.assertTrue(actual_result.ok)