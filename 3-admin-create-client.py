"""
    Create a new client.
    This example requires environment variables GL_STAGE and GL_APIKEY to be set.
    Only a apikey user with admin privileges can run this example.
"""

import json
import os

from faker import Faker
fake = Faker()

from greenlight import GreenLight

try:
    glapi = GreenLight(os.environ['GL_STAGE'], os.environ['GL_APIKEY'])
except ValueError as err:
    print("GreenLight object failed to initialize.  Are environment variables GL_STAGE and GL_APIKEY set correctly?")
    print("Error code was:", err)
    quit()

new_client_name = fake.company()
your_client_id = fake.uuid4()

resp = glapi.create_client(
    name=new_client_name,
    countries={'US': 'active'},
    currencies={'USD': 'active'},
    job_policies={
        'w2_only': False,            # set True if client requires all workers to be EoR
        'individual_po': False,      # set True if worker can only be started after valid PO is provided
        'bg_check': False,           # set True if client policy requires background check for workers
        # 'bg_check_type': 'basic'   # ignored if bg_check is False.  Legal values are 'basic' and 'enhanced'
        'drug_check': False          # set True if client policy requires drug screening for workers
    },
    # ext_id_scope='NameOfPartner',  # your ext_id_scope (optional). if left blank, your greenlight id will be used.
    ext_id=your_client_id         # your unique identifier for this client
)

print(json.dumps(resp, indent=2))

