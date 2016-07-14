import json
import requests
import compat

import config
config.load_settings()

def get_job_list():
    host = config.settings['host']
    user_api_key = config.settings['user_api_key']
    url = compat.urlunparse(('http', host, '/api/v1/datasets/evaluation/pending-jobs', '', '', ''))
    headers = {'Authorization': 'Token ' + user_api_key}
    response = requests.get(url, headers=headers)
    return response.json()

def run_jobs():
    jobs = get_job_list()
    print(jobs)
