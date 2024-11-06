import paramiko
import subprocess
import os

def push_file(filename):
    # Define the server and authentication details
    hostname = os.getenv('HOSTNAME')  # Replace with your server's IP address or hostname
    port = os.getenv('PORT')                            # Default SSH port
    username = os.getenv('USERNAME')           # Replace with your username
    password = os.getenv('PASSWORD')           # Replace with your password (or use a private key)

    # Define local and remote file paths
    local_file_path = f'/opt/airflow/dags/{filename}.py'  # Path to the local file you want to upload
    remote_file_path = f'/home/ubuntu/booksy-boostedchat-deployment/boostedchat-site/dags/{filename}.py'  # Path on the remote server where the file will be uploaded

    try:
        # Create an SSH client instance
        ssh = paramiko.SSHClient()

        # Automatically add untrusted hosts (use with caution)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the server
        ssh.connect(hostname=hostname, port=port, username=username, password=password)

        # Open an SFTP session
        sftp = ssh.open_sftp()

        # Upload the file
        sftp.put(local_file_path, remote_file_path)
        print(f"Successfully copied {local_file_path} to {remote_file_path}")

        # Close the SFTP session and SSH connection
        sftp.close()
        ssh.close()

    except Exception as e:
        print(f"Error: {e}")

def push_file_gcp(filename):
    command = [
        "gcloud", "compute", "scp",
        "--zone=us-east1-b",
        "--project=boostedchatapi",
        "--ssh-key-file=/home/martin/.ssh/google_compute_engine",
        f"/opt/airflow/dags/{filename}.py",
        "root@apiboostedchat-vm:/root/boostedchat-site/dags"
    ]

    try:
        subprocess.run(command, check=True)
        print("File transfer successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during file transfer: {e}")
