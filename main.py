from pfsh_parser.sftp_engine import sftp_connect
from pfsh_parser.csv_engine import daily_inventory_parser, order_parser
from pfsh_parser.log_engine import LogEngine

from pfsh_parser.creds import (
    PFSH_USERNAME,
    PFSH_PASSWORD,
    HOST,
    BASE_INVENTORY_FILE,
    UPDATED_INVENTORY_FILE,
    MASTER_INVENTORY_FILE,
    BASE_ORDERS_FILE,
    UPDATED_ORDERS_FILE,
    LOG_FILE,
)

import time

username = PFSH_USERNAME
password = PFSH_PASSWORD
host = HOST

# LOCAL_FILE,REMOTE_FILE,LOG_FILE
# get latest inventory File
logger = LogEngine(file_path=LOG_FILE)
logger.log(f"PULLING BASE INVENTORY FILE FROM SFTP")
sftp_connect(
    host=host,
    port=22,
    username=username,
    password=password,
    direction="pull",
    # GRAB THE FILE AND SAVE A COPY TO LOCAL FILES DIR
    remote_file=f"Inventory/{BASE_INVENTORY_FILE}",
    local_file=f"files/{BASE_INVENTORY_FILE}",
)
logger.log(f"ATTEMPING FILE PARSING")
# modify file for matrixify
daily_inventory_parser(f"files/{BASE_INVENTORY_FILE}", f"files/{MASTER_INVENTORY_FILE}")
logger.log("PUTTING MODIFIED FILE ON SFTP")
# Put modified file on sftp server
time.sleep(1)
sftp_connect(
    host=HOST,
    port=22,
    username=username,
    password=password,
    direction="push",
    local_file=f"files/tmp/{UPDATED_INVENTORY_FILE}",
    remote_file=f"imports/inventory/{UPDATED_INVENTORY_FILE}",
)
logger.log("GRABBING EXPORTED ORDERS FILE FROM SFTP")
# grab orders
time.sleep(1)
sftp_connect(
    host=host,
    port=22,
    username=username,
    password=password,
    direction="pull",
    local_file=f"files/tmp/{BASE_ORDERS_FILE}",
    remote_file=f"exports/orders/{BASE_ORDERS_FILE}",
)
logger.log(f"PARSE AND MODIFY ORDERS FILE")
# parse orders
order_parser(f"files/tmp/{BASE_ORDERS_FILE}")
logger.log(f"PUSH MODIFIED ORDERS FILE TO SFTP")
# push new orders
time.sleep(1)
sftp_connect(
    host=host,
    port=22,
    username=username,
    password=password,
    direction="push",
    local_file=f"files/tmp/{UPDATED_ORDERS_FILE}",
    remote_file=f"Orders/JCBEAN_ORDERS.csv",
)
