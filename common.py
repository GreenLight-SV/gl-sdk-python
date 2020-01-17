import json
import os
import datetime
from faker import Faker
fake = Faker('en_US')

DEBUG = False

DEFAULT_COUNTRIES = {'US': 'active', 'GB': 'active'}
DEFAULT_CURRENCIES = {'USD': 'active', 'GBP': 'active'}
DEFAULT_JOB_POLICIES = {
    'w2_only': False, 
    'individual_po': False, 
    'bg_check': False, 
    'bg_check_type': 'n/a',
    'drug_check': False
}
DEPARTMENTS = [
    'HR', 'R&D', 'Finance', 'Sales', 'Marketing', 'Operations'
]



# create fake data

def random_client(admin):
    client = {
        'name': fake.company(),
        'countries': admin['countries'],   # change to subset if client is limited to certain countries
        'currencies': admin['currencies'], # change to subset if client is limited to certain currencies
        'job_policies': DEFAULT_JOB_POLICIES,
        'ext_id': fake.uuid4()             # put your client identifier here
    }
    return client

def random_project(client):
    client_name = client['name']
    random_words = [fake.word().capitalize(), fake.word().capitalize()]
    project_name = f'Project {random_words[0]}{random_words[1]}'
    description = f'Do work on {project_name} for {client_name}'
    your_id = fake.uuid4()  # replace with your unique project identifier 

    return {
        'client_id': client['id'],
        'name': project_name,
        'description': description,
        'ext_id': your_id
    }

def random_position(client):
    pay_type = 'h'      # h for hourly, s for flat rate or by deliverable
    title = fake.job()
    department = fake.word(ext_word_list = DEPARTMENTS)
    description = fake.paragraph()
    start_date = datetime.date.today()

    end_date = start_date.replace(
        month = (start_date.month + 6) % 12,
        year = start_date.year + (1 if (start_date.month > 5) else 0)
    )

    return {
        'client_id': client['id'],
        'department': department,
        'title': title,
        'description': description,
        'start_date': start_date,
        'end_date': end_date,                   # optional
        'work_location_type': 'offsite',        # onsite or offsite
        # 'work_location_onsite_id': xxxxx,     # address id; required if onsite
        'work_timezone': 'America/New_York',
        # 'hm_id': xxxxx,
        'classify_client_pref': 'w2-only',
        'pay_type': pay_type,
        'rate_currency': 'USD',
        'country': 'US',
    }

def random_worker():
    worker = {
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'phone': '+16175551212' # ISO format
    }
    email = worker['first_name'] + worker ['last_name'] + '@' + 'contractmagician.com'
    worker['email'] = email
    return worker

def random_payrate(project_id):
    return {
        'project_id': project_id, 
        'rate_currency': 'USD', 
        'rate': fake.random_int(25, 150)
    }

def random_your_id(): return fake.uuid4()[:8]

def choose_existing_job(greenlight):
    role_type = greenlight.role_type()

    if role_type == 'client':
        client_id = greenlight.client['id']
        selected_job = choose_client_job(greenlight, client_id)
        if selected_job:
            return selected_job 
        else:
            print("Client " + client_to_string(greenlight.client) + " has no active job.  Onboard & approve a worker then try again.")
            quit()
        return selected_job

    if role_type == 'admin':
        clients = greenlight.get_admin_clients()
        if len(clients) == 0:
            print("There are no clients.  Add a client and try again.")
            quit()
        for client in clients:
            if DEBUG: print("Looking for jobs in client " + client_to_string(client))
            selected_job = choose_client_job(greenlight, client['id'])
            if selected_job: return selected_job

        print("There are no active jobs for any client.  Onboard & approve a worker then try again.")
        quit()

def choose_client_job(greenlight, client_id):
    active_jobs = greenlight.get_client_active_jobs(client_id)
    if len(active_jobs) == 0: return None
    return active_jobs[0] # arbitrarily use the first job (which may vary, as list order is not guaranteed)


# for printing to console
#
def jsonprint(x):
    print(json.dumps(x, indent=2))

def print_header(path):
    scriptname = os.path.basename(path)
    print("\n" + scriptname + "\n" + "-" * len(scriptname))

def worker_to_string(worker):
    name = worker['first_name'] + ' ' + worker['last_name']
    email = worker['email']
    phone = worker['phone']
    return f"'{name}' ({email}) {phone}"

def project_to_string(project):
    project_name = project['name']
    project_id = project['id']
    return f"'{project_name}' id={project_id}"

def position_to_string(position):
    id = position['id']
    title = position['title']
    return f"'{title}' id={id}"

def job_to_string(job):
    id = job['id']
    title = job['title']
    if not 'user' in job:
        return f"'{title}' job_id={id}"
    user = job['user']
    name = user['first_name'] + " " + user['last_name']
    return f"{name} '{title}' job_id={id}"


def client_to_string(client):
    return client['name']

