import json
import os
from faker import Faker
fake = Faker()

DEFAULT_COUNTRIES = {'US': 'active', 'GB': 'active'}
DEFAULT_CURRENCIES = {'USD': 'active', 'GBP': 'active'}
DEFAULT_JOB_POLICIES = {
    'w2_only': False, 
    'individual_po': False, 
    'bg_check': False, 
    'bg_check_type': 'n/a',
    'drug_check': False
}

def jsonprint(x):
    print(json.dumps(x, indent=2))

def print_header(path):
    scriptname = os.path.basename(path)
    print("\n" + scriptname + "\n" + "-" * len(scriptname))

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
    your_id = fake.uuid4()

    return {
        'client_id': client['id'],
        'name': project_name,
        'description': description,
        'ext_id': your_id
    }

def random_position():
    pass