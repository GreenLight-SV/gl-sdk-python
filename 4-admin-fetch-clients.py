"""
    Examples of how to fetch all clients, and how to fetch one client by greenlight id or by your id.
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

# a) list all clients associated with the admin for this apikey
clients = glapi.get_admin_clients()
print('\nExample a)')
print(json.dumps(clients, indent=2))

if len(clients) == 0:
    print('The rest of this example is not interesting if the client list is empty - create some clients and try again.')
    quit()
    
# b) fetch a client by greenlight id
desired_client_id = clients[0]['id']         # for demonstration purposes
client = glapi.get_client(desired_client_id)
print('\nExample b)')
print(f'client for id {desired_client_id} is:')
print(json.dumps(client, indent=2))

# c) fetch a client by your id
your_client_id = clients[-1]['ext_id']       # for demonstration purposes
your_id_scope = clients[-1]['ext_id_scope']  # for demonstration purposes
client = glapi.get_client(your_client_id, scope=your_id_scope)
print('\nExample c)')
print(f'client for your id {your_client_id} is:')
print(json.dumps(client, indent=2))



