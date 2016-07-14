from __future__ import print_function

import json
import os
import sys
import requests
import compat

try:
    import requests
except ImportError:
    from .vendor import requests

import config
config.load_settings()

def get_job_list():
    host = config.settings['host']
    user_api_key = config.settings['user_api_key']
    url = compat.urlunparse(('http', host, '/api/v1/datasets/evaluation/pending-jobs', '', '', ''))
    headers = {'Authorization': 'Token ' + user_api_key}
    response = requests.get(url, headers=headers)
    return response.json()

if __name__ == '__main__':
    jobs = get_job_list()
