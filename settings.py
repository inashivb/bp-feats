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
USER_NAME = "current"
