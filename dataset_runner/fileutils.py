import re
import json
import unicodedata

def get_job_details():
    f = open("job.json",'r')
    f = f.read()
    return json.loads(f)

def load_low_level(recording):
    f = open(recording+".json",'r')
    f = f.read()
    return json.loads(f)[recording]

def create_snapshot(dataset):
    snapshot = {
        "name": dataset["name"],
        "description": dataset["description"],
        "classes": [{
            "name": c["name"],
            "description": c["description"],
            "recordings": c["recordings"],
        } for c in dataset["classes"]],
    }
    return snapshot

def _slugify(string):
    """Converts unicode string to lowercase, removes alphanumerics and
    underscores, and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    """
    print(string)
    string = unicodedata.normalize('NFKD', string).encode('ascii', 'ignore').decode('ascii')
    print(string)
    string = re.sub('[^\w\s-]', '', string).strip().lower()
    print('I am returning')
    return re.sub('[-\s]+', '-', string)

