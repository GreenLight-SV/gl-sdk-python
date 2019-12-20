"""
    Verify that GreenLight api can authenticate with provided apikey.
    This example requires environment variables GL_STAGE and GL_APIKEY to be set.

    As client: you can run this example.
    As admin: you can run this example.
"""

from greenlight import GreenLight, get_glapi_from_env
glapi = get_glapi_from_env()

if glapi.profile:
    print("GreenLight API '" + glapi.stage + "' is alive and authenticated successfully.")
    print("Your apikey is associated with: ")
    print(f"  role={glapi.profile['role']}")
    print(f"  admin={glapi.admin['name']}")
    if (glapi.client and 'name' in glapi.client): 
        print(f"  client={glapi.client['name']}") 
else:
    print("GreenLight object initialized, but its role is empty.  The user associated with your apikey may be misconfigured.  Contact support.")


