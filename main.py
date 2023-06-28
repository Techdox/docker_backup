import paramiko
import os

# Constants for SSH connection details
REMOTE_HOSTNAME = '192.168.68.109'
REMOTE_PORT = 22  # SSH default port
REMOTE_USERNAME = 'techdox'
PRIVATE_KEY_PATH = '/Users/nick/.ssh/id_rsa'

def run_backup(container_name, backup_file_name, backup_path, local_destination):
    # Command to execute on the remote server to stop the Docker container
    stop_command = f'docker stop {container_name}'

    # Command to execute on the remote server to start the Docker container
    start_command = f'docker start {container_name}'

    # Command to execute on the remote server to create the backup
    backup_command = f'docker run --rm --volumes-from {container_name} -v $(pwd):/backup ubuntu bash -c "cd {backup_path} && tar cvf /backup/{backup_file_name}.tar ."'

    # Create an SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Load the private key
    private_key = paramiko.RSAKey.from_private_key_file(PRIVATE_KEY_PATH)

    try:
        # Connect to the remote server using key-based authentication
        ssh_client.connect(REMOTE_HOSTNAME, REMOTE_PORT, REMOTE_USERNAME, pkey=private_key)

        # Execute the command to stop the Docker container
        ssh_client.exec_command(stop_command)
        print("Docker container stopped.")

        # Execute the backup command on the remote server
        stdin, stdout, stderr = ssh_client.exec_command(backup_command)
        print(stdout.read().decode())
        
        # Print the standard error
        print(stderr.read().decode())

        # Create an SCP client from the SSH client
        scp_client = ssh_client.open_sftp()

        # Retrieve the home directory of the remote user
        remote_home_directory = ssh_client.exec_command('echo $HOME')[1].read().decode().strip()

        # Construct the remote backup file path
        remote_backup_file_path = os.path.join(remote_home_directory, f'{backup_file_name}.tar')

        # Construct the local backup file path
        local_backup_file_path = os.path.join(local_destination, f'{backup_file_name}.tar')

        # Download the backup file from the remote server to the local machine
        scp_client.get(remote_backup_file_path, local_backup_file_path)
        print("Backup file downloaded successfully.")

        # Execute the command to start the Docker container
        ssh_client.exec_command(start_command)
        print("Docker container started.")

    finally:
        # Close the SCP client
        scp_client.close()
        
        # Close the SSH connection
        ssh_client.close()

def get_user_input():
    container_name = input("Enter the container name to backup: ")
    backup_file_name = input("Enter the backup file name: ")
    backup_path = input("Enter the backup path: ")
    local_destination = input("Enter the local destination path to save the backup file: ")

    return container_name, backup_file_name, backup_path, local_destination

def main():
    container_name, backup_file_name, backup_path, local_destination = get_user_input()
    run_backup(container_name, backup_file_name, backup_path, local_destination)

if __name__ == '__main__':
    main()
