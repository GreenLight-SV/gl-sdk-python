"""
    Verify that GreenLight api is alive for selected stage.
    This example requires environment variable GL_STAGE to be set.
    It does not authenticate, so GL_APIKEY is not required, and if present it is ignored.
"""

# setting up the example
import sys
import os
import common
common.print_header(__file__)

# real stuff starts here
from greenlight import GreenLight

try:
    greenlight = GreenLight(os.environ['GL_STAGE'])
    api_hash = greenlight.get_api_hash()
    print("GreenLight API '" + greenlight.stage + "' is alive and returns hash=" + api_hash)

except (KeyError, ValueError) as err:
    print("GreenLight object failed to initialize.  Is environment variable GL_STAGE set correctly?")
    print("Error code was:", err)
    sys.exit(1)

except:
    print("Unexpected error initializing GreenLight object:", sys.exc_info()[0])
    raise
