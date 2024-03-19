import os

try:
    PFSH_USERNAME = os.environ["PFSH_USERNAME"]
    PFSH_PASSWORD = os.environ["PFSH_PASSWORD"]
    HOST = USERNAME = os.environ["HOST"]
    BASE_INVENTORY_FILE = os.environ["BASE_INVENTORY_FILE"]
    MASTER_INVENTORY_FILE = os.environ["MASTER_INVENTORY_FILE"]
    UPDATED_INVENTORY_FILE = os.environ["UPDATED_INVENTORY_FILE"]
    BASE_ORDERS_FILE = os.environ["BASE_ORDERS_FILE"]
    UPDATED_ORDERS_FILE = os.environ["UPDATED_ORDERS_FILE"]
    LOG_FILE = os.environ["LOG_FILE"]
except KeyError:
    raise Exception("VALUES NOT FOUND")
