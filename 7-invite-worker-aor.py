"""
    A script to invite a new worker for AoR (independent contractor), who will receive email invitation to onboard him/herself.
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
    
###### Invite an independent contractor worker: in 4 acts ######

def create_ic_position(act_number, answer_value):
    ## Scene 1. Create a basic position, including job title, job description, work location.
    new_position = common.random_position(client, 'ic-only')
    your_position_id = common.random_your_id()

    gl_position_id = greenlight.create_position(new_position, your_position_id)['id']
    position = greenlight.get_position(gl_position_id)
    print(f"{act_number}.1 Created a position " + common.position_to_string(position))

    ## Scene 2. Fetch the client-side IC classification questions, and answer them
    position_questions = greenlight.get_questions_for_client(gl_position_id)

    answers = [{'question_id': q['id'], 'answer': answer_value} for q in position_questions]  
    greenlight.add_position_answers(position, answers)
    print(f"{act_number}.2 Fetched and answered " + str(len(position_questions)) + " mandatory questions before inviting worker")

    ## Scene 3. Check if the worker is eligible to go through IC classification
    position = greenlight.get_position(gl_position_id)
    classify_client_result = position['classify_client_result']
    if classify_client_result == 'w2-or-ic':
        print(f"{act_number}.3 This position may be a valid IC, depending on information supplied by the worker")
    elif classify_client_result == 'w2-only':
        print(f"{act_number}.3 Based on the answers provided, this position can only be onboarded under employee status")
    else:
        print(f"{act_number}.3 classify_client_result was " + classify_client_result)

    ## Scene 4. Invite a worker to the position.
    new_worker = common.random_worker()

    your_worker_id = common.random_your_id()
    new_worker['ext_id_scope'] = your_scope
    new_worker['ext_id'] = your_worker_id
    your_job_id = common.random_your_id()

    pay_by_project = [common.random_payrate(gl_project_id)]

    job = greenlight.invite_worker(position, new_worker, pay_by_project, your_job_id)
    print(f"{act_number}.4 Invited worker " + common.worker_to_string(new_worker) + " to job " + common.job_to_string(job))


your_scope = greenlight.scope() 

# Act I: Decide what client the worker should be invited to
client = common.choose_existing_client(greenlight)
print(f"  I.  This IC worker will be invited for client " + common.client_to_string(client))

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

project = greenlight.get_project(id=gl_project_id)
print(f" II.  Created new project " + common.project_to_string(project))

## Act III. Create a position that MAY be an independent contractor, depending on worker's information
create_ic_position("III", answer_value=False)

## Act IV. Create a position that MAY be an independent contractor, depending on worker's information
create_ic_position(" IV", answer_value=True)







