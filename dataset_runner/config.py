import os
import sys
import os.path
import compat
import ConfigParser

settings = {}


def load_settings():
    defaultfile = os.path.join(os.path.dirname(__file__), "default.conf")
    config = compat.RawConfigParser()
    config.read(defaultfile)
    settings["host"] = config.get("acousticbrainz", "host")
    try:
        settings["user_api_key"] = config.get("user", "api_key")
    except ConfigParser.NoOptionError:
        print('Please put your API key in the config file')
        sys.exit(0)
