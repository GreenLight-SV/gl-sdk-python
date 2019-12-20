from .common import get_base_url
from urllib.parse import urlencode
from urllib.error import HTTPError
import os
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
        quit()

class GreenLight():
    """GreenLight API client"""

    def __init__(self, stage: str, apikey: str = ''):
        self.stage = stage
        self.apikey = apikey
        self.admin = {}
        self.client = {}
        if apikey: self.profile = self.get_profile()

    def role_type(self):
        role = self.profile['role']
        if (role[0:2] == 'gl'): return "admin"
        if (role[0:2] == 'cl'): return "client"
        return "unknown"
    
    def get_api_url(self, path_relative: str, queryparams: dict):
        url = get_base_url(self.stage).strip('/') + '/' + path_relative.strip('/')
        querystring = ('?' + urlencode(queryparams)) if queryparams else ''
        return url + querystring

    def request(
        self, 
        path_relative: str, 
        method: str = 'GET', 
        queryparams: dict = {}, 
        expected_status: int = 0, 
        body: dict = {}
    ):
        url = self.get_api_url(path_relative, queryparams)
        headers = {'x-api-key': self.apikey}
        method = method.upper()

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
            raise ValueError(f'Invalid status code {resp.status_code} returned from {method} {url}: {resp.text}')
        return resp.json() if resp.status_code != 204 else {}

    def get_api_hash(self):
        version_json = self.request('/version')
        return version_json['git_hash']

    def get_admin(self, admin_id):
        full_admin = self.request(f'/admin/{admin_id}')
        return full_admin

    def get_client(self, client_id, scope = None):
        queryparams = {'scope': scope} if scope else {}
        full_client = self.request(f'/client/{client_id}', queryparams=queryparams)
        return full_client

    def delete_client(self, client_id):
        resp = self.request(
            f'/client/{client_id}', method='DELETE')
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
        full_clients = self.request(f'/admin/{admin_id}/clients', queryparams={'status': 'current'})
        clients = list(map(client_fields, full_clients))
        return clients

    def create_client(
        self, 
        name, 
        countries = DEFAULT_COUNTRIES, 
        currencies = DEFAULT_CURRENCIES, 
        job_policies = DEFAULT_JOB_POLICIES,
        ext_id_scope = None,
        ext_id = None
    ):
        if (self.profile['resource'] != 'admin'):
            raise ValueError('Logged in user does not have sufficient permission to create client')
        body = {
            'name': name,
            'countries': countries,
            'currencies': currencies,
            'job_policies': job_policies,
            'admin_id': self.admin['id']
        }
        if ext_id:
            body['ext_id_scope'] = ext_id_scope or (self.profile['resource'] + ':' + self.profile['resource_id'])
            body['ext_id'] = ext_id

        resp = self.request('/client', method='POST', body=body)
        return resp

    def get_profile(self):
        profiles_json = self.request('/profile')
        if (len(profiles_json) != 1):
            raise ValueError(f'Your API user is has {len(profiles_json)} profiles.  Please contact support.')
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
