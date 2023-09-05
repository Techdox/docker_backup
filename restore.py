import paramiko

# Constants for SSH connection details
REMOTE_HOSTNAME = ''
REMOTE_PORT = 22  # SSH default port
REMOTE_USERNAME = ''
PRIVATE_KEY_PATH = ''

def run_remote_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    print(stdout.read().decode())
    print(stderr.read().decode())

def main():
    # Get user input
    container_name = input("Enter the container name to restore: ")
    backup_file_name = input("Enter the backup file name: ")
    backup_path = input("Enter the backup path: ")
    backup_source = input("Enter the backup source on the remote server: ")

    # Create an SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Load the private key
        private_key = paramiko.RSAKey.from_private_key_file(PRIVATE_KEY_PATH)

        # Connect to the remote server using key-based authentication
        ssh_client.connect(REMOTE_HOSTNAME, REMOTE_PORT, REMOTE_USERNAME, pkey=private_key)

        # Commands
        stop_command = f'docker stop {container_name}'
        start_command = f'docker start {container_name}'
        restore_command = (
            f'docker run --rm --volumes-from {container_name} '
            f'-v {backup_source}:/backup ubuntu bash -c '
            f'"rm -rf {backup_path}/* && cd {backup_path} && tar xvf /backup/{backup_file_name}.tar"'
        )

        # Execute commands
        run_remote_command(ssh_client, stop_command)
        print("Docker container stopped.")
        run_remote_command(ssh_client, restore_command)
        run_remote_command(ssh_client, start_command)
        print("Docker container started.")

    finally:
        # Close the SSH connection
        ssh_client.close()

if __name__ == '__main__':
    main()
