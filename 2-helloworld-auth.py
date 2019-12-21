"""
    Verify that GreenLight api can authenticate with provided apikey.
    This example requires environment variables GL_STAGE and GL_APIKEY to be set.

    As client: you can run this example.
    As admin: you can run this example.
"""

# setting up the example
import common
common.print_header(__file__)

# real stuff starts here
from greenlight import GreenLight, get_glapi_from_env
greenlight = get_glapi_from_env()

if greenlight.profile:
    print("GreenLight API '" + greenlight.stage + "' is alive and authenticated successfully.")
    print("Your apikey is associated with: ")
    print(f"  role={greenlight.profile['role']}")
    print(f"  admin={greenlight.admin['name']}")
    if (greenlight.client and 'name' in greenlight.client): 
        print(f"  client={greenlight.client['name']}") 
else:
    print("GreenLight object initialized, but its role is empty.  The user associated with your apikey may be misconfigured.  Contact support.")


