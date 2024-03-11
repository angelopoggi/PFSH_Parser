import os

try:
    PFSH_USERNAME = os.environ["PFSH_USERNAME"]
    PFSH_PASSWORD = os.environ["PFSH_PASSWORD"]
    HOST = USERNAME = os.environ["HOST"]
    LOCAL_FILE = os.environ["LOCAL_FILE"]
    REMOTE_FILE = os.environ["REMOTE_FILE"]
    LOG_FILE = os.environ["LOG_FILE"]
except KeyError:
    raise Exception("VALUES NOT FOUND")