"""
    Create a new client.
    This example requires environment variables GL_STAGE and GL_APIKEY to be set.

    As client: you CANNOT run this example, it is for admin roles only.
    As admin: you can run this example.
"""

## setting up the example
import common
common.print_header(__file__)

## real stuff starts here
from greenlight import GreenLight, get_glapi_from_env
greenlight = get_glapi_from_env()
if greenlight.role_type() != 'admin':
    raise ValueError('This example can only be run with admin credentials')

new_client = common.random_client(greenlight.admin)
your_client_id = common.random_your_id()
gl_client_id = greenlight.create_client(new_client, your_client_id)['id']

# fetch back, just to show how it's done
client = greenlight.get_client(gl_client_id)
print("Created client " + common.client_to_string(client))

