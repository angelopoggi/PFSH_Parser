from pfsh_parser.sftp_engine import sftp_connect
from pfsh_parser.csv_engine import daily_inventory_parser, order_parser
from pfsh_parser.log_engine import LogEngine

from pfsh_parser.creds import (
    PFSH_USERNAME,
    PFSH_PASSWORD,
    HOST,
    UPDATED_ORDERS_FILE,
    LOG_FILE,
    SHOP_NAME,
    SHOPIFY_ACCESS_TOKEN,
)

import time

username = PFSH_USERNAME
password = PFSH_PASSWORD
host = HOST

logger = LogEngine(file_path=LOG_FILE)
logger.log(f"Fetching Orders from Shopify API")
order_parser(SHOP_NAME, "unfulfilled", SHOPIFY_ACCESS_TOKEN)
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
    remote_file=f"Orders/POSTFORDERS.csv",
)
