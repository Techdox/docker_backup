import paramiko
import os

# SSH connection details
remote_hostname = ''
remote_port = 22  # SSH default port
remote_username = ''
private_key_path = ''

# Inputs for container name, backup file name, and backup path
container_name = input("Enter the container name to backup: ")
backup_file_name = input("Enter the backup file name: ")
backup_path = input("Enter the backup path: ")

# Command to execute on the remote server to stop the Docker container
stop_command = f'docker stop {container_name}'

# Command to execute on the remote server to start the Docker container
start_command = f'docker start {container_name}'

# Command to execute on the remote server to create the backup
backup_command = f'docker run --rm --volumes-from {container_name} -v $(pwd):/backup ubuntu bash -c "cd {backup_path} && tar cvf /backup/{backup_file_name}.tar ."'

# Local destination path to save the backup file
local_destination = input("Enter the local destination path to save the backup file: ")

# Create an SSH client
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Load the private key
    private_key = paramiko.RSAKey.from_private_key_file(private_key_path)

    # Connect to the remote server using key-based authentication
    ssh_client.connect(remote_hostname, remote_port, remote_username, pkey=private_key)

    # Execute the command to stop the Docker container
    ssh_client.exec_command(stop_command)
    print("Docker container stopped.")

    # Execute the backup command on the remote server
    stdin, stdout, stderr = ssh_client.exec_command(backup_command)
    print(stdout.read().decode())

    # Create an SCP client from the SSH client
    scp_client = ssh_client.open_sftp()

    # Retrieve the home directory of the remote user
    remote_home_directory = ssh_client.exec_command('echo $HOME')[1].read().decode().strip()

    # Construct the remote backup file path
    remote_backup_file_path = os.path.join(remote_home_directory, f'{backup_file_name}.tar')

    # Construct the local backup file path
    local_backup_file_path = os.path.join(local_destination, f'{backup_file_name}.tar')

    # Download the backup file from the remote server to the local server
    scp_client.get(remote_backup_file_path, local_backup_file_path)
    print("Backup file downloaded successfully.")

    # Execute the command to start the Docker container
    ssh_client.exec_command(start_command)
    print("Docker container started.")

    # Close the SCP client
    scp_client.close()

finally:
    # Close the SSH connection
    ssh_client.close()
