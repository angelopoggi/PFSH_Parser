import paramiko
from pfsh_parser.creds import LOG_FILE
from pfsh_parser.log_engine import LogEngine

def sftp_connect(host,port,username,password,direction,local_file=None,remote_file=None):
    logger = LogEngine(file_path=LOG_FILE)
    transport = paramiko.Transport(str(host),int(port))
    transport.connect(username=str(username), password=str(password))
    sftp = paramiko.SFTPClient.from_transport(transport)

    #Download or upload a file depending on direction
    logger.log("PULLING DAILY INVENTORY UPDATE FILE FROM SFTP")
    if direction == "pull":
        print(f"Pulling file {remote_file} to {local_file}")
        sftp.get(remote_file, local_file)
    else:
        logger.log("PUSHING UPDATED INVENTORY FILE TO SFTP")
        print(f"Pushing file {local_file} to {remote_file}")
        sftp.put(local_file, remote_file)

    # Close the SFTP session and transport
    sftp.close()
    transport.close()
