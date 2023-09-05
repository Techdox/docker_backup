import paramiko
import os

# Constants for SSH connection details
REMOTE_HOSTNAME = ''
REMOTE_PORT = 22  # SSH default port
REMOTE_USERNAME = ''
PRIVATE_KEY_PATH = ''

def run_remote_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    print(stdout.read().decode())
    print(stderr.read().decode())

def backup_container(container_name, backup_file_name, backup_path, local_destination):
    # Commands
    stop_command = f'docker stop {container_name}'
    start_command = f'docker start {container_name}'
    backup_command = (
        f'docker run --rm --volumes-from {container_name} '
        f'-v $(pwd):/backup ubuntu bash -c '
        f'"cd {backup_path} && tar cvf /backup/{backup_file_name}.tar ."'
    )

    # Create an SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Load the private key
        private_key = paramiko.RSAKey.from_private_key_file(PRIVATE_KEY_PATH)

        # Connect to the remote server using key-based authentication
        ssh_client.connect(REMOTE_HOSTNAME, REMOTE_PORT, REMOTE_USERNAME, pkey=private_key)

        # Execute commands
        run_remote_command(ssh_client, stop_command)
        print("Docker container stopped.")
        run_remote_command(ssh_client, backup_command)
        run_remote_command(ssh_client, start_command)
        print("Docker container started.")

        # Construct remote and local file paths
        remote_backup_file_path = os.path.join(ssh_client.exec_command('echo $HOME')[1].read().decode().strip(), f'{backup_file_name}.tar')
        local_backup_file_path = os.path.join(local_destination, f'{backup_file_name}.tar')

        # Create an SCP client from the SSH client
        scp_client = ssh_client.open_sftp()

        # Download the backup file from the remote server to the local machine
        scp_client.get(remote_backup_file_path, local_backup_file_path)
        print("Backup file downloaded successfully.")

    finally:
        # Close the SCP client and SSH connection
        scp_client.close()
        ssh_client.close()

def get_user_input():
    container_name = input("Enter the container name to backup: ")
    backup_file_name = input("Enter the backup file name: ")
    backup_path = input("Enter the backup path: ")
    local_destination = input("Enter the local destination path to save the backup file: ")

    return container_name, backup_file_name, backup_path, local_destination

def main():
    container_name, backup_file_name, backup_path, local_destination = get_user_input()
    backup_container(container_name, backup_file_name, backup_path, local_destination)

if __name__ == '__main__':
    main()
