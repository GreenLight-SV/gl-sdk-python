from .common import get_base_url, format_date, jsonprint
from urllib.parse import urlencode
from urllib.error import HTTPError
import os
import sys
import requests
import json

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
        clients = list(map(client_fields, full_clients))
        return clients

    def create_client(self, client): 
        if (self.role_type() != 'admin'):
            raise ValueError('Logged in user does not have sufficient permission to create client')

        client['admin_id'] = self.admin['id']

        resp = self.__request('/client', method='POST', body=client)
        return resp

    def create_project(self, project):
        resp = self.__request('/project', method='POST', body=project)
        return resp

    def create_position(self, position):
        position['start_date'] = format_date(position['start_date'])
        if 'end_date' in position: position['end_date'] = format_date(position['end_date'])
        resp_add = self.__request('/position', method='POST', body=position)
        position_id = resp_add['id']
        self.__request(f'/position/{position_id}/action/approve', method='POST', expected_status=200)
        return resp_add

    def invite_worker(self, position, worker, pay_by_project, your_scope = None, your_job_id = None):
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
        return job

    ## private methods
    def __fetch_endpoint(self, endpoint, id, scope = None):
        queryparams = {'scope': scope} if scope else {}
        record = self.__request(f'/{endpoint}/{id}', queryparams=queryparams)

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
            'resource_id': full_profile['resource_id']
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
