"""
    A script to invite a new worker for EoR, who will receive email invitation to onboard him/herself.
    This example sets client-specified information (pay rate, project, onsite/offsite, etc.) and pre-populates 
    some worker-specified information (name, mailing address, phone, etc.).

    This example requires environment variables GL_STAGE and GL_APIKEY to be set.

    As client: you can run this example to create a worker for your client.
    As admin: you can run this example, which will select one of your clients and assign the worker to that client.
"""

import common

from greenlight import GreenLight, get_glapi_from_env
glapi = get_glapi_from_env()

def select_client():
    role_type = glapi.role_type()

    if role_type == 'client':
        selected_client = glapi.client
        return selected_client['id']

    if role_type == 'admin':
        clients = glapi.get_admin_clients()
        if len(clients) == 0:
            print("I can't add a worker without at least one client.  Add client(s) and try again.")
            quit()
        selected_client = clients[0]  # arbitrarily use the first client (which may vary, as list order is not guaranteed)
        return selected_client['id']

    raise ValueError(f'Unsupported role type {role_type}')

def random_project():
    pass

def random_position():
    pass
    
# Invite a worker
client_id = select_client()
print(f'Selected client {client_id}')
