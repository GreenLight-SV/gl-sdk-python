from .common import get_base_url, format_date, jsonprint
from urllib.parse import urlencode
from urllib.error import HTTPError
import os
import sys
import requests
import json
from datetime import date, timedelta

VERBOSE = False

DEFAULT_COUNTRIES = {'US': 'active', 'GB': 'active'}
DEFAULT_CURRENCIES = {'USD': 'active', 'GBP': 'active'}
DEFAULT_JOB_POLICIES = {
    'w2_only': False, 
    'individual_po': False, 
    'bg_check': False, 
    'bg_check_type': 'n/a',
    'drug_check': False
}

def get_glapi_from_env():
    try:
        glapi = GreenLight(os.environ['GL_STAGE'], os.environ['GL_APIKEY'])
        return glapi

    except (KeyError, ValueError) as err:
        print("GreenLight object failed to initialize.  Are environment variables GL_STAGE and GL_APIKEY set correctly?")
        print("Error code was:", err)
        sys.exit(1)

class GreenLight():
    """GreenLight API client"""

    def __init__(self, stage: str, apikey: str = ''):
        self.stage = stage
        self.apikey = apikey
        self.admin = {}
        self.client = {}
        if apikey: self.profile = self.__get_profile()

    def role_type(self):
        role = self.profile['role']
        if (role[0:2] == 'gl'): return "admin"
        if (role[0:2] == 'cl'): return "client"
        return None

    def scope(self):
        if self.role_type() == 'admin':
            return self.admin['ext_id_scope']
        if self.role_type() == 'client':
            return self.client['ext_id_scope']
        return None

    def get_api_hash(self):
        version_json = self.__request('/version')
        return version_json['git_hash']

    def get_position(self, id, scope = None): return self.__fetch_endpoint('position', id, scope)
    def get_client(self, id, scope = None): return self.__fetch_endpoint('client', id, scope)
    def get_admin(self, id, scope = None): return self.__fetch_endpoint('admin', id, scope)
    def get_project(self, id, scope = None): return self.__fetch_endpoint('project', id, scope)
    def get_job(self, id, scope = None): return self.__fetch_endpoint('job', id, scope)
    def get_job_extended(self, id): return self.__fetch_endpoint('job', id, None, {'extended': 'true'})

    def delete_client(self, id):
        resp = self.__request(f'/client/{id}', method='DELETE')
        return resp

    def get_admin_clients(self):
        def client_fields(client):
            return {
                'name': client['name'],
                'id': client['id'],
                'ext_id_scope': client['ext_id_scope'],
                'ext_id': client['ext_id']
            }
        admin_id = self.admin['id']
        full_clients = self.__request(f'/admin/{admin_id}/clients', queryparams={'status': 'current'})
        clients = [client_fields(client) for client in full_clients]
        return clients

    def get_client_active_jobs(self, client_id):
        def job_fields(job):
            return {
                'title': job['title'],
                'id': job['id'],
                'ext_id_scope': job['ext_id_scope'],
                'ext_id': job['ext_id']
            }
        full_jobs = self.__request(f'/client/{client_id}/jobs', queryparams={'status': 'active'})
        jobs = [job_fields(job) for job in full_jobs]
        return jobs

    def get_questions_for_client(self, position_id = None):
        def question_fields(question):
            return {
                'title': question['title'],
                'answer_type': question['answer_type'],
                'help_text': question['help_text'],
                'id': question['id']
            }
        admin_id = self.admin['id']
        path = f'/question?form_type=job_classification_client&admin={admin_id}'
        if position_id: path += f'&position={position_id}'
        full_questions = self.__request(path)
        questions = [question_fields(question) for question in full_questions]

        return questions

    def get_job_projects(self, job_id):
        full_projects = self.__request(f'/job/{job_id}/projects')
        return full_projects

    def get_background_check_status(self, job_id, scope = None):
        if scope:
            gl_job_id = self.get_job(job_id, scope=scope)['id']
        else:
            gl_job_id = job_id
        job_extended = self.get_job_extended(gl_job_id)
        onboarding = job_extended['onboarding']
        w2_path = onboarding['w2_path']
        background_check_status = w2_path['background_check']
        return background_check_status

    def create_client(self, client, your_client_id): 
        if (self.role_type() != 'admin'):
            raise ValueError('Logged in user does not have sufficient permission to create client')

        client['admin_id'] = self.admin['id']
        if your_client_id:
            client['ext_id'] = your_client_id
            client['ext_id_scope'] = self.scope()

        resp = self.__request('/client', method='POST', body=client)
        return resp

    def create_project(self, project):
        resp = self.__request('/project', method='POST', body=project)
        return resp

    def update_job(self, job):
        id = job['id']
        resp = self.__request(f'/job/{id}', method='PUT', body=job)
        return resp

    def create_position(self, position, your_position_id = None):
        position['start_date'] = format_date(position['start_date'])
        if 'end_date' in position: position['end_date'] = format_date(position['end_date'])
        if your_position_id:
            position['ext_id'] = your_position_id
            position['ext_id_scope'] = self.scope()
        resp_add = self.__request('/position', method='POST', body=position)
        position_id = resp_add['id']
        self.__request(f'/position/{position_id}/action/approve', method='POST', expected_status=200)
        return resp_add

    def add_position_answers(self, position, answers):
        position['classify_client_answers'] = {'answers': answers}
        position_id = position['id']
        resp_put = self.__request(f'/position/{position_id}', method='PUT', body=position)
        return resp_put

    def invite_worker(self, position, worker_details, pay_by_project, your_job_id = None):
        worker = worker_details['worker']
        address = worker_details['address'] if 'address' in worker_details else None
        invite = {
            'position_id': position['id'],
            'start_date': position['start_date'],
            'first_name': worker['first_name'],
            'last_name': worker['last_name'],
            'email': worker['email'],
            'phone': worker['phone'],
            'projects': pay_by_project
        }
        if 'end_date' in position: invite['end_date'] = position['end_date']

        resp = self.__request('/job_invite', method='POST', body=invite)
        gl_job_id = resp['id']
        job = self.get_job(gl_job_id)

        # add ext_id into the job if provided
        if your_job_id:
            job['ext_id_scope'] = self.scope()
            job['ext_id'] = your_job_id
            self.update_job(job)

        # persist contractor address if provided
        if address:
            contractor_id = job['contractor_id']
            self.create_address(address, "contractor", contractor_id)

        return job

    def create_address(self, address, ref_type, ref_id):
        address['ref_type'] = ref_type
        address['ref_id'] = ref_id 
        address['kind'] = 'l'
        address['name'] = 'Mailing'
        return self.__request('/address', method='POST', body=address)['id']

    def get_client_addresses(self, client_id):
        return self.__request(f'/client/{client_id}/addresses', method='GET')

    def create_timesheet_with_shifts_expenses(self, shifts_expenses, your_timesheet_id = None, approve=False):
        shifts = shifts_expenses['shifts']
        expenses = shifts_expenses['expenses']
        period_ending = self.__calculate_period_ending(shifts=shifts)
        job_id = shifts[0]['job_id']
        timesheet_id = self.__create_timesheet(job_id, period_ending, your_timesheet_id)
        for shift in shifts:
            self.__add_shift_to_timesheet(shift, timesheet_id)
        for expense in expenses:
            self.__add_expense_to_timesheet(expense, timesheet_id)

        self.__submit_timesheet(timesheet_id)
        if approve:
            self.__approve_timesheet(timesheet_id)
        return timesheet_id

    def create_timesheet_with_deliverables(self, deliverables, your_timesheet_id = None, approve=False):
        period_ending = self.__calculate_period_ending(deliverables=deliverables)
        job_id = deliverables[0]['job_id']
        timesheet_id = self.__create_timesheet(job_id, period_ending, your_timesheet_id)
        for deliverable in deliverables:
            self.__add_deliverable_to_timesheet(deliverable, timesheet_id)

        self.__submit_timesheet(timesheet_id)
        if approve:
            self.__approve_timesheet(timesheet_id)
        return timesheet_id

    ## private methods
    def __create_timesheet(self, job_id, period_ending, your_timesheet_id):
        timesheet = {
            'job_id': job_id,
            'period_ending': period_ending
        }
        if your_timesheet_id:
            timesheet['ext_id'] = your_timesheet_id
            timesheet['ext_id_scope'] = self.scope()

        return self.__request('/timesheet', method='POST', body=timesheet)['id']
    
    def __submit_timesheet(self, timesheet_id):
        return self.__request(f'/timesheet/{timesheet_id}/action/submit', method='POST', expected_status=200)

    def __approve_timesheet(self, timesheet_id):
        return self.__request(f'/timesheet/{timesheet_id}/action/approve', method='POST', expected_status=200)

    def __add_shift_to_timesheet(self, shift, timesheet_id):
        shift['timesheet_id'] = timesheet_id
        return self.__request('/shift', method='POST', body=shift)['id']

    def __add_expense_to_timesheet(self, expense, timesheet_id):
        expense['timesheet_id'] = timesheet_id
        return self.__request('/expense', method='POST', body=expense)['id']

    def __add_deliverable_to_timesheet(self, deliverable, timesheet_id):
        deliverable['timesheet_id'] = timesheet_id
        return self.__request('/deliverable', method='POST', body=deliverable)['id']

    def __calculate_period_ending(self, shifts=[], deliverables=[]):
        def first_sunday_on_or_after(dt):
            days_to_go = 6 - dt.weekday()
            if days_to_go:
                dt += timedelta(days_to_go)
            return dt

        if len(shifts):
            last_time_in = max([shift['time_in'] for shift in shifts])

        if len(deliverables):        
            last_deliverable = max([deliverable['date'] for deliverable in deliverables])

        if len(shifts) and len(deliverables):
            last_date_string = max([last_time_in, last_deliverable])
        elif len(shifts):
            last_date_string = last_time_in
        elif len(deliverables):
            last_date_string = last_deliverable
        else:
            return "2019-12-31T22:59:59"

        last_date = date.fromisoformat(last_date_string[:10])
        timezone_offset = last_time_in[-6:] if len(shifts) else "-05:00"
        period_ending_date = first_sunday_on_or_after(last_date)

        # This sample application does not handle DST, so we cheat and set period_ending
        # to 10:59pm Sunday rather than 11:59.  That way it's still within the week when DST is active.
        period_ending = period_ending_date.isoformat() + "T22:59:59" + timezone_offset
        return period_ending

    def __fetch_endpoint(self, endpoint, id, scope = None, queryparams = {}):
        allparams = queryparams.copy()
        if scope: allparams['scope'] = scope
        record = self.__request(f'/{endpoint}/{id}', queryparams=allparams)

        # in future this will return only relevant fields; for now it returns everything
        return record   

    def __get_api_url(self, path_relative: str, queryparams: dict):
        url = get_base_url(self.stage).strip('/') + '/' + path_relative.strip('/')
        querystring = ('?' + urlencode(queryparams)) if queryparams else ''
        return url + querystring

    def __request(
        self, 
        path_relative: str, 
        method: str = 'GET', 
        queryparams: dict = {}, 
        expected_status: int = 0, 
        body: dict = {}
    ):
        url = self.__get_api_url(path_relative, queryparams)
        headers = {'x-api-key': self.apikey}
        method = method.upper()

        if VERBOSE: print(method, url)

        if ('ext_id' in body) and not ('ext_id_scope' in body and body['ext_id_scope']):
            body['ext_id_scope'] = self.scope()

        if method == 'GET':
            if expected_status == 0: expected_status = 200
            resp = requests.get(url, headers=headers)
        elif method == 'POST':
            if expected_status == 0: expected_status = 201
            resp = requests.post(url, json=body, headers=headers)
        elif method == 'DELETE':
            if expected_status == 0: expected_status = 204
            resp = requests.delete(url, headers=headers)
        elif method == 'PUT':
            if expected_status == 0: expected_status = 204
            resp = requests.put(url, json=body, headers=headers)
        else:
            raise ValueError(f'Unsupported http method {method}')

        if (resp.status_code != expected_status):
            raise ValueError(f'Unexpected status code {resp.status_code} returned from {method} {url}: {resp.text}')

        return resp.json() if resp.status_code != 204 else {}

    def __get_profile(self):
        profiles_json = self.__request('/profile')
        if (len(profiles_json) != 1):
            raise ValueError(f'Your API user has {len(profiles_json)} profiles, but should have exactly 1.  Please contact support.')
        full_profile = profiles_json[0]
        profile = {
            'role': full_profile['role'],
            'resource': full_profile['resource'],
            'resource_id': full_profile['resource_id'],
            'user_id': full_profile['user_id'] if 'user_id' in full_profile else None
        }

        if (profile['resource'] == 'admin'):
            self.admin = self.get_admin(profile['resource_id'])
            self.client = {}
        elif (profile['resource'] == 'client'):
            self.client = self.get_client(profile['resource_id'])
            self.admin = self.get_admin(self.client['admin_id'])
        else:
            raise ValueError('API is only supported for admin or client user types')

        return profile
