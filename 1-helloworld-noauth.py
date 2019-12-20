"""
    Verify that GreenLight api is alive for selected stage.
    This example requires environment variable GL_STAGE to be set.
    It does not authenticate, so GL_APIKEY is ignored.
"""

import json
import os

from greenlight import GreenLight

try:
    glapi = GreenLight(os.environ['GL_STAGE'])
    api_hash = glapi.get_api_hash()
    print("GreenLight API '" + glapi.stage + "' is alive and returns hash=" + api_hash)

except:
    print("GreenLight object failed to initialize.  Is environment variable GL_STAGE set correctly?")