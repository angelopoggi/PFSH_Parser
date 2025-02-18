import os

try:
    PFSH_USERNAME = os.environ["PFSH_USERNAME"]
    PFSH_PASSWORD = os.environ["PFSH_PASSWORD"]
    HOST = os.environ["HOST"]
    BASE_INVENTORY_FILE = os.environ["BASE_INVENTORY_FILE"]
    MASTER_INVENTORY_FILE = os.environ["MASTER_INVENTORY_FILE"]
    UPDATED_INVENTORY_FILE = os.environ["UPDATED_INVENTORY_FILE"]
    BASE_ORDERS_FILE = os.environ["BASE_ORDERS_FILE"]
    UPDATED_ORDERS_FILE = os.environ["UPDATED_ORDERS_FILE"]
    LOG_FILE = os.environ["LOG_FILE"]
    SHOP_NAME = os.environ["SHOP_NAME"]
    SHOPIFY_ACCESS_TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"]
    SHIPPING_FILE = os.environ["SHIPPING_FILE"]
    EMAIL_SENDER = os.environ["EMAIL_SENDER"]
    EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
    RECIPIENT_LIST = os.environ["RECIPIENT_LIST"]
    EMAIL_SERVER = os.environ["EMAIL_SERVER"]
    EMAIL_PORT = os.environ["EMAIL_PORT"]
except KeyError:
    raise Exception("VALUES NOT FOUND")
