import json
import os
import datetime
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
DEPARTMENTS = [
    'HR', 'R&D', 'Finance', 'Sales', 'Marketing', 'Operations'
]

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
    your_id = fake.uuid4()  # replace with your unique position identifier

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
        'ext_id': your_id
    }

def random_worker():
    return {}
