from pfsh_parser.sftp_engine import sftp_connect
from pfsh_parser.csv_engine import shipping_parser
from pfsh_parser.log_engine import LogEngine

from pfsh_parser.creds import (
    PFSH_USERNAME,
    PFSH_PASSWORD,
    HOST,
    LOG_FILE,
    SHOP_NAME,
    SHOPIFY_ACCESS_TOKEN,
    SHIPPING_FILE,
)

import time

username = PFSH_USERNAME
password = PFSH_PASSWORD
host = HOST

logger = LogEngine(file_path=LOG_FILE)
logger.log(f"PULLING SHIPPING FILE")

time.sleep(1)
sftp_connect(
    host=host,
    port=22,
    username=username,
    password=password,
    direction="pull",
    local_file=f"files/tmp/{SHIPPING_FILE}",
    remote_file=f"Shipping/{SHIPPING_FILE}",
)
logger.log("UPDATING TRACKING INFORMATION FROM CSV TO SHOPIFY")
# update Tracking information
shipping_parser(f"files/tmp/{SHIPPING_FILE}", SHOP_NAME, SHOPIFY_ACCESS_TOKEN)
