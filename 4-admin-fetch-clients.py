"""
    Examples of how to fetch all clients, and how to fetch one client by greenlight id or by your id.
    This example requires environment variables GL_STAGE and GL_APIKEY to be set.

    As client: you CANNOT run this example, it is for admin roles only.
    As admin: you can run this example.
"""

# setting up the example
import common
common.print_header(__file__)

# real stuff starts here

from greenlight import GreenLight, get_glapi_from_env
greenlight = get_glapi_from_env()
if greenlight.role_type() != 'admin':
    raise ValueError('This example can only be run with admin credentials')

# a) list all clients associated with the admin for this apikey
clients = greenlight.get_admin_clients()
print('\nExample a)')
common.jsonprint(clients)

if len(clients) == 0:
    print('The rest of this example is not interesting if the client list is empty - create some clients and try again.')
    quit()
    
# b) fetch a client by greenlight id
desired_client_id = clients[0]['id']         # for demonstration purposes
client = greenlight.get_client(desired_client_id)
print('\nExample b)')
print(f'client for id {desired_client_id} is:')
common.jsonprint(client)

# c) fetch a client by your id
def has_ext_id(client): return ('ext_id' in client) and client['ext_id']
clients_with_ext_id = list(filter(has_ext_id, clients))
if len(clients_with_ext_id):
    your_client_id = clients_with_ext_id[-1]['ext_id'] # for demonstration purposes; normally you already know this
    your_id_scope = greenlight.scope()
    client = greenlight.get_client(your_client_id, scope=your_id_scope)
    print('\nExample c)')
    print(f'client for your id {your_client_id} is:')
    common.jsonprint(client)



