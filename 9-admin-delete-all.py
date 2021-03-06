"""
    A script to delete all clients, to clean up the staging database if it gets too crowded.
    This script will also be extended in future to delete projects and workers.
    Also shows how to delete a single client, project, or worker.
    In general this is NOT RECOMMENDED.  
    But if you have created a lot of example clients for testing you may want to clean up.
    This example requires environment variables GL_STAGE and GL_APIKEY to be set.

    As client: you CANNOT run this example, it is for admin roles only.
    As admin: you can run this example.  Only in stage=staging though.
"""

# setting up the example
import common
common.print_header(__file__)

i_am_sure = input("are you sure? ")
if not i_am_sure in "yY":
    exit()

# real stuff starts here
from greenlight import GreenLight, get_glapi_from_env
greenlight = get_glapi_from_env()
if greenlight.role_type() != 'admin':
    raise ValueError('This example can only be run with admin credentials')

if greenlight.stage == 'production' or greenlight.stage == 'beta' or greenlight.stage == 'site':
    raise EnvironmentError('Running this example in production is a Really Bad Idea.')

clients = greenlight.get_admin_clients()
if len(clients) == 0:
    print('There are no clients to delete.')
    quit()
    
for client in clients:
    name = client['name']
    print(f"Deleting client '{name}'")
    greenlight.delete_client(client['id'])

clients_after = greenlight.get_admin_clients()
if len(clients_after) == 0:
    print('All clients successfully deleted.')
else:
    print(f'{len(clients_after)} of {len(clients)} not deleted:')
    common.jsonprint(clients_after)
    raise ValueError('Delete failed')



