import paramiko
import os

# Constants for SSH connection details
REMOTE_HOSTNAME = ''
REMOTE_PORT = 22  # SSH default port
REMOTE_USERNAME = ''
PRIVATE_KEY_PATH = ''

def run_restore(container_name, backup_file_name, backup_path, backup_source):
    # Command to execute on the remote server to stop the Docker container
    stop_command = f'docker stop {container_name}'

    # Command to execute on the remote server to start the Docker container
    start_command = f'docker start {container_name}'

    # Command to execute on the remote server to restore the backup
    restore_command = f'docker run --rm --volumes-from {container_name} -v {backup_source}:/backup ubuntu bash -c "rm -rf {backup_path}/* && cd {backup_path} && tar xvf /backup/{backup_file_name}.tar"'

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

        # Execute the restore command on the remote server
        stdin, stdout, stderr = ssh_client.exec_command(restore_command)
        print(stdout.read().decode())

        # Print the standard error
        print(stderr.read().decode())

        # Execute the command to start the Docker container
        ssh_client.exec_command(start_command)
        print("Docker container started.")

    finally:
        # Close the SSH connection
        ssh_client.close()

def get_user_input():
    container_name = input("Enter the container name to restore: ")
    backup_file_name = input("Enter the backup file name: ")
    backup_path = input("Enter the backup path: ")
    backup_source = input("Enter the backup source on the remote server")

    return container_name, backup_file_name, backup_path, backup_source

def main():
    container_name, backup_file_name, backup_path, backup_source = get_user_input()
    run_restore(container_name, backup_file_name, backup_path, backup_source)

if __name__ == '__main__':
    main()
