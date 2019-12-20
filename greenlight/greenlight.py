from .common import get_base_url
from urllib.parse import urlencode
from urllib.error import HTTPError
import requests
import json

class GreenLight():
    """GreenLight client"""

    def __init__(self, stage: str, apikey: str = ''):
        self.stage = stage
        self.apikey = apikey
        if apikey: self.profile = self.get_profile()

    
    def get_api_url(self, path_relative: str, queryparams: dict):
        url = get_base_url(self.stage).strip('/') + '/' + path_relative.strip('/')
        querystring = ('?' + urlencode(queryparams)) if queryparams else ''
        return url + querystring


    def request(
        self, 
        path_relative: str, 
        method: str = 'GET', 
        queryparams: dict = {}, 
        authenticated: bool = False, 
        expected_status: int = 200, 
        body: dict = {}
    ):
        url = self.get_api_url(path_relative, queryparams)
        headers = {'x-api-key': self.apikey}
        resp = requests.get(
            url,
            headers=headers
        )
        if (resp.status_code != expected_status):
            raise ValueError(f'Invalid status code {resp.status_code} returned from {method} {url}')
        return resp.json()

    def get_api_hash(self):
        version_json = self.request('/version')
        return version_json['git_hash']

    def get_profile(self):
        profiles_json = self.request('/profile')
        if (len(profiles_json) != 1):
            raise ValueError('Your API user is misconfigured.  Please contact support.')
        profile = profiles_json[0]
        return {
            'role': profile['role'],
            'resource': profile['resource'],
            'resource_id': profile['resource_id']
        }
