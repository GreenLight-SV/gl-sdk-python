"""
    A script to invite a new worker for EoR, who will receive email invitation to onboard him/herself.
    This example sets client-specified information (pay rate, project, onsite/offsite, etc.) and pre-populates 
    some worker information (name, email, phone).
    It also creates a new project for the worker, though in reality you might re-use an existing project.

    This example requires environment variables GL_STAGE and GL_APIKEY to be set.

    As client: you can run this example to create a worker for your client.
    As admin: you can run this example, which will select one of your clients and assign the worker to that client.
"""

# setting up the example
import common
common.print_header(__file__)

# real stuff starts here
from greenlight import GreenLight, get_glapi_from_env
greenlight = get_glapi_from_env()
    
###### Invite an employee worker: in 5 acts ######

# You can reference any record using its native (greenlight) id value (field 'id'),
# or you can reference it using your own id value that you store as 'ext_id' at creation time.
# In order to use your id, you have to qualify it with a scope. 
# Your scope is permanent and stable, so you make it part of your app configuration; 
# you can also retrieve it from your client or admin record, which is what we do here.
your_scope = greenlight.scope() 

# Act I: Decide what client the worker should be invited to
client = common.choose_existing_client(greenlight)
print(f"  I. This EE worker will be invited for client " + common.client_to_string(client))

# Act II: Determine what project (ie billing code) this assignment will be billed to.
# When you create the job, it's required to have at least one GreenLight project id.
# - In this example we are creating a new project.
# - If you have a project already, and you know its GreenLight id, just use that.
# - If you have a project already but don't know its GreenLight id, you can fetch it using get_project(your_id, your_scope).
new_project = common.random_project(client)  # create test data

your_project_id = common.random_your_id()    # normally this would be your identifier
new_project['ext_id_scope'] = your_scope
new_project['ext_id'] = your_project_id

gl_project_id = greenlight.create_project(new_project)['id']  # create function returns {'id': project_id}

# Example of how you can fetch this project using your identifier
project = greenlight.get_project(id=your_project_id, scope=your_scope)
print(f" II. Created new project " + common.project_to_string(project))

## Act III. Create a position, including job title, job description, work location.

# get an address id to make this an onsite position
client_addresses = greenlight.get_client_addresses(client['id'])
onsite_id = client_addresses[0]['id'] if len(client_addresses) else None
new_position = common.random_position(
    client, 
    classify_client_pref = 'w2-only', 
    hourly = True, 
    onsite_id = onsite_id,
    hm_id = greenlight.profile['user_id']  # set the APIuser as the hiring manager 
)

your_position_id = common.random_your_id()
gl_position_id = greenlight.create_position(new_position, your_position_id)['id']

# Example of how you can fetch this position using native identifier
position = greenlight.get_position(gl_position_id)
print(f"III. Created a position " + common.position_to_string(position))

## Act IV. Invite a worker to the position.
new_worker = common.random_worker()
your_job_id = common.random_your_id()
pay_by_project = [common.random_pay(gl_project_id, hourly = True)]

job = greenlight.invite_worker(position, new_worker, pay_by_project, your_job_id)
print(" IV. Invited worker " + common.worker_to_string(new_worker['worker']) + " to job " + common.job_to_string(job))

## Act V. Poll for background check status of worker

background_check_status = greenlight.get_background_check_status(your_job_id, scope=your_scope)
print("  V. Background check status is: ", background_check_status)




