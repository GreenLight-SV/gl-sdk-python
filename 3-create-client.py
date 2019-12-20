"""
    Create a new client.
    This example requires environment variables GL_STAGE and GL_APIKEY to be set.
"""

import json
import os
import sys

from faker import Faker
fake = Faker()

from greenlight import GreenLight

try:
    glapi = GreenLight(os.environ['GL_STAGE'], os.environ['GL_APIKEY'])
except ValueError as err:
    print("GreenLight object failed to initialize.  Are environment variables GL_STAGE and GL_APIKEY set correctly?")
    print("Error code was:", err)
    quit()

name = fake.company()
# name = 'TestClient'
resp = glapi.create_client(name)
client_id = resp['id']
clients = glapi.get_admin_clients()
print(json.dumps(clients, indent=2))

