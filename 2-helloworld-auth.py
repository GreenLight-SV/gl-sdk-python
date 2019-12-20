"""
    Verify that GreenLight api can authenticate with provided apikey.
    This example requires environment variables GL_STAGE and GL_APIKEY to be set.
"""

import json
import os

from greenlight import GreenLight

try:
    glapi = GreenLight(os.environ['GL_STAGE'], os.environ['GL_APIKEY'])
    if glapi.profile:
        print("GreenLight API '" + glapi.stage + "' is alive and authenticated successfully.")
        print("Your apikey is associated with: " + json.dumps(glapi.profile))
    else:
        print("GreenLight object initialized, but its role is empty.  The user associated with your apikey may be misconfigured.  Contact support.")

except (KeyError, ValueError):
    print("GreenLight object failed to initialize.  Are environment variables GL_STAGE and GL_APIKEY set correctly?")
