import json
import os
import datetime
from faker import Faker
import random
fake = Faker('en_US')

DEBUG = True

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

def random_position(client, classify_client_pref):
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
        # 'hm_id': xxxxx,                       # greenlight ID of the hiring manager (person who approves timesheets)
        'classify_client_pref': classify_client_pref,
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

    # optional fields
    state = fake.state_abbr()
    zip = fake.postcode_in_state(state_abbr = state)
    address = {
        'street': fake.street_address(),
        'city': fake.city(),
        'state': state,
        'zip': zip,
        'country': 'US'
    }

    return {'worker': worker, 'address': address}

def random_payrate(project_id):
    return {
        'project_id': project_id, 
        'rate_currency': 'USD', 
        'rate': fake.random_int(25, 150)
    }

def random_your_id(): return fake.uuid4()[:8]

def random_deliverables(job_id, project_id):
    def make_deliverable(y, m, d, description, currency, amount):
        date = f"{y:04d}-{m:02d}-{d:02d}"
        return {
            'date': date,
            'description': description, 
            'currency': currency,
            'amount': amount,
            'job_id': job_id,
            'project_id': project_id
        }
    year = random.choice([2018, 2019, 2020])
    month = random.randrange(12) + 1
    day = random.randrange(25)

    return [make_deliverable(year, month, day, f"Deliverable {i}", "USD", random.randrange(1000, 25000)) for i in range(3)]

def random_shifts_expenses(job_id, project_id):
    def make_shift(y, m, d, start, minutes):
        start_time_iso = f"{y:04d}-{m:02d}-{d:02d}T{start}"
        return {
            'time_in': start_time_iso, 
            'minutes': minutes,
            'job_id': job_id,
            'project_id': project_id
        }

    def make_expense(y, m, d, description, currency, amount):
        expense_date = f"{y:04d}-{m:02d}-{d:02d}"
        return {
            'expense_date': expense_date, 
            'description': description,
            'currency': currency,
            'amount': amount,
            'job_id': job_id,
            'project_id': project_id
        }

    year = random.choice([2018, 2019, 2020])
    month = random.randrange(12) + 1
    start_day = random.randrange(25)

    # we will create shifts for 8:30am-12:30pm and 1:00pm-5:30pm, in EST time (-0500), on three successive days
    sample_morning_start_CST = '08:30:00-05:00'
    sample_morning_minutes = 240 # 4 hours from 8:30-12:30
    sample_afternoon_start_CST = '13:00:00-05:00'
    sample_afternoon_minutes = 270 # 4.5 hours from 1:00-5:30
    
    mornings = [make_shift(year, month, day, sample_morning_start_CST, sample_morning_minutes) for day in range(start_day, start_day + 3)]
    afternoons = [make_shift(year, month, day, sample_afternoon_start_CST, sample_afternoon_minutes) for day in range(start_day, start_day + 3)]
    shifts = mornings + afternoons
    expenses = [make_expense(year, month, start_day, f"Sample expense {i}", "USD", random.randrange(0, 500)) for i in range(4)]
    return {'shifts': shifts, 'expenses': expenses}

def choose_existing_client(greenlight):
    role_type = greenlight.role_type()

    if role_type == 'client':
        return greenlight.client

    if role_type == 'admin':
        clients = greenlight.get_admin_clients()
        if len(clients) == 0:
            print("There are no clients.  Add a client and try again.")
            quit()
        return random.choice(clients)

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
            selected_job = choose_client_job(greenlight, client['id'])
            if selected_job: return selected_job

        print("There are no active jobs for any client.  Onboard & approve a worker then try again.")
        quit()

def choose_client_job(greenlight, client_id):
    active_jobs = greenlight.get_client_active_jobs(client_id)
    if len(active_jobs) == 0: return None
    return random.choice(active_jobs) # arbitrarily use the first job (which may vary, as list order is not guaranteed)

def choose_existing_project(greenlight, job_id):
    job_projects = greenlight.get_job_projects(job_id)
    return random.choice(job_projects)


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


