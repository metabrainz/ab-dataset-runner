import os
import os.path
import compat

settings = {}
def load_settings():
    defaultfile = os.path.join(os.path.dirname(__file__), "default.conf")
    config = compat.RawConfigParser()
    config.read(defaultfile)
    settings["host"] = config.get("acousticbrainz", "host")
    settings["user_api_key"] = config.get("user", "api_key")
