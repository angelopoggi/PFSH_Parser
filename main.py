from pfsh_parser.sftp_engine import sftp_connect
from pfsh_parser.csv_engine import daily_inventory_parser
from pfsh_parser.creds import PFSH_USERNAME,PFSH_PASSWORD,HOST,LOCAL_FILE,REMOTE_FILE,LOG_FILE
import time

#get latest file
sftp_connect(host=HOST,
             port=22,
             username=PFSH_USERNAME,
             password=PFSH_PASSWORD,
             direction="pull",
             remote_file=REMOTE_FILE,
             local_file=f"{LOCAL_FILE}.csv")

#modify file for matrixify
daily_inventory_parser(f"{LOCAL_FILE}.csv")

#Put modified file on sftp server
time.sleep(1)
sftp_connect(host=HOST,
             port=22,
             username=PFSH_USERNAME,
             password=PFSH_PASSWORD,
             direction="push",
             local_file=f"{LOCAL_FILE}.csv",
             remote_file=f"{REMOTE_FILE}")

#Put Logs on server
time.sleep(1)
sftp_connect(host=HOST,
             port=22,
             username=PFSH_USERNAME,
             password=PFSH_PASSWORD,
             direction="push",
             local_file=LOG_FILE,
             remote_file=f"Log_Files/{LOG_FILE}")
