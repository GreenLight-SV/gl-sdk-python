"""
    Example of how to upload time, expenses, deliverables for a worker.
    This example requires environment variables GL_STAGE and GL_APIKEY to be set.
    It also requires that there be at least one job in active state.

    To put a job into active state, you must:
     1. Invite a worker, to create the job 
     2. Login as that invited worker and complete onboarding steps
     3. Login as admin and approve the worker (Evaluations page)

    As client: you can run this example, if your client already has an active job.
    As admin: you can run this example.
"""

# setting up the example
import common
common.print_header(__file__)

# real stuff starts here
from greenlight import GreenLight, get_glapi_from_env
greenlight = get_glapi_from_env()
your_scope = greenlight.scope() 

###### Add hours for a worker ######

# Act I: Decide what client and job the hours will be added to
job = common.choose_existing_job(greenlight)
job_ext = greenlight.get_job_extended(job['id'])
print(f"  I. Hours will be added for " + common.job_to_string(job_ext))
