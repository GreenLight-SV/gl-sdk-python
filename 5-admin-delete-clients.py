"""
    A script to delete all clients; also shows how to delete a single client.
    In general this is NOT RECOMMENDED.  
    But if you have created a lot of example clients for testing you may want to clean up.
    This example requires environment variables GL_STAGE and GL_APIKEY to be set.
    Only an apikey user with admin privileges can run this example.
"""

import json
import os

from greenlight import GreenLight

try:
    glapi = GreenLight(os.environ['GL_STAGE'], os.environ['GL_APIKEY'])
except ValueError as err:
    print("GreenLight object failed to initialize.  Are environment variables GL_STAGE and GL_APIKEY set correctly?")
    print("Error code was:", err)
    quit()

if glapi.stage == 'production':
    raise EnvironmentError("Running this example in production is a Really Bad Idea.")

# fetch all clients associated with the admin for this apikey
clients = glapi.get_admin_clients()
if len(clients) == 0:
    print('There are no clients to delete.')
    quit()
    
# iterate through clients deleting them
for client in clients:
    name = client['name']
    print(f'Deleting client {name}')
    glapi.delete_client(client['id'])

clients_after = glapi.get_admin_clients()
if len(clients_after) == 0:
    print('All clients successfully deleted.')
else:
    print(f'{len(clients_after)} of {len(clients)} not deleted:')
    print(json.dumps(clients_after, indent=2))
    raise ValueError('Delete failed')



