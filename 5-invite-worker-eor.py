"""
    A script to invite a new worker for EoR, who will receive email invitation to onboard him/herself.
    This example sets client-specified information (pay rate, project, onsite/offsite, etc.) and pre-populates 
    some worker-specified information (name, mailing address, phone, etc.).
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
glapi = get_glapi_from_env()

def select_client():
    role_type = glapi.role_type()

    if role_type == 'client':
        selected_client = glapi.client
        return selected_client

    if role_type == 'admin':
        clients = glapi.get_admin_clients()
        if len(clients) == 0:
            print("I can't add a worker without at least one client.  Add client(s) and try again.")
            quit()
        selected_client = clients[0]  # arbitrarily use the first client (which may vary, as list order is not guaranteed)
        return selected_client

    raise ValueError(f'Unsupported role type {role_type}')
    
###### Invite a worker: in 4 acts ######

# Act I: Decide what client the worker should be invited to
client = select_client()
client_name = client['name']
print(f"  I. This worker will be invited for client='{client_name}'")

# Act II: Determine what project (ie billing code) this assignment will bill to.
# When you create the job, it's required to have at least one GreenLight project id.
# - In this example we are creating a new project.
# - If you have a project already, and you know its GreenLight id, just use that.
# - If you have a project already but don't know its GreenLight id, you can fetch it using get_project(your_id, your_scope).
new_project = common.random_project(client)
new_project_name = new_project['name']
resp = glapi.create_project(new_project)

# You don't need to fetch back the project using your identifier,
# but we do it here just to show how it's done
your_id = new_project['ext_id']
your_scope = glapi.scope()
project = glapi.get_project(id=your_id, scope=your_scope)
project_name = project['name']
project_id = project['id']
print(f" II. Created new project '{project_name}' id={project_id}")

## 

