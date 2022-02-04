import sys

REDMINE_URL = "https://redmine.openinfosecfoundation.org"

def get_api_key():
    try:
        with open("api.keys", "r") as f:
            key = f.readline().strip()
    except OSError as e:
        print(e)
        key = None
    return key

REDMINE_KEY = get_api_key()
PROJECT_VERSION = "6.0.5"
PROJECT_NAME = "suricata"
USER_NAME = "current"
PRIVATE = 0  # Only 0,1 values seem to work, True, False do not
