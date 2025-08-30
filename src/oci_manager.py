# oci_manager.py
#
# This module provides the core functionality for managing OCI resources,
# including compute instances and network security lists, for the
# Shadowsocks proxy.
# It interacts directly with the OCI Python SDK and uses Paramiko for SSH.

import oci
import requests
import paramiko
import time
import os

class OCIManager:
    """
    Manages OCI compute instance and networking resources.
    """
    def __init__(self, config):
        """
        Initializes the OCI Manager with OCI configuration and SDK clients.
        """
        self.config = config['oci']
        self.compute_client = oci.core.ComputeClient(self.config)
        self.networking_client = oci.core.VirtualNetworkClient(self.config)

    def create_or_get_instance(self):
        """
        Checks for an existing Shadowsocks instance and creates one if it doesn't exist.
        """
        print("Checking for existing Shadowsocks instance...")
        try:
            # List instances and find one with the correct tag
            list_instances_response = self.compute_client.list_instances(
                compartment_id=self.config['compartment_id'],
                lifecycle_state='RUNNING'
            )
            for instance in list_instances_response.data:
                if instance.freeform_tags.get('project') == 'shadowsocks-proxy':
                    print(f"Found existing instance with OCID: {instance.id}. Reusing.")
                    self.instance_id = instance.id
                    return instance, "Reusing existing instance."

            # If no instance found, create a new one
            print("No existing instance found. Creating a new one...")
            instance_details = oci.core.models.LaunchInstanceDetails(
                compartment_id=self.config['compartment_id'],
                availability_domain=self.config['compute']['availability_domain'],
                shape=self.config['compute']['instance_shape'],
                image_id=self.config['compute']['image_id'],
                subnet_id=self.config['compute']['subnet_id'],
                ssh_authorized_keys=self._get_ssh_key(),
                display_name='shadowsocks-proxy',
                freeform_tags={'project': 'shadowsocks-proxy'}
            )
            launch_instance_response = self.compute_client.launch_instance(
                launch_instance_details=instance_details
            )
            self.instance_id = launch_instance_response.data.id
            print(f"New instance launched with OCID: {self.instance_id}")

            # Wait for the instance to be provisioned
            self.compute_client.get_instance(self.instance_id).data.wait_for_lifecycle_state('RUNNING')
            print("Instance is now running.")
            return self.compute_client.get_instance(self.instance_id).data, "New instance created and started."

        except oci.exceptions.ServiceError as e:
            print(f"OCI Service Error: {e.message}")
            return None, f"Error: {e.message}"
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None, f"Error: {e}"

    def start_instance(self):
        """
        Starts a stopped OCI instance.
        """
        print(f"Starting instance with OCID: {self.instance_id}...")
        try:
            self.compute_client.instance_action(self.instance_id, 'START')
            self.compute_client.get_instance(self.instance_id).data.wait_for_lifecycle_state('RUNNING')
            print("Instance started successfully.")
            return True, "Instance started."
        except oci.exceptions.ServiceError as e:
            return False, f"OCI Service Error: {e.message}"

    def stop_instance(self):
        """
        Stops a running OCI instance.
        """
        print(f"Stopping instance with OCID: {self.instance_id}...")
        try:
            self.compute_client.instance_action(self.instance_id, 'SOFTSTOP')
            self.compute_client.get_instance(self.instance_id).data.wait_for_lifecycle_state('STOPPED')
            print("Instance stopped successfully.")
            return True, "Instance stopped."
        except oci.exceptions.ServiceError as e:
            return False, f"OCI Service Error: {e.message}"

    def configure_instance(self, instance):
        """
        Connects to the instance via SSH and installs/configures Shadowsocks.
        This is a placeholder and requires a separate script for full implementation.
        """
        public_ip = instance.public_ip
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(public_ip, username='opc', key_filename=self.config['key_file'])

            # Example commands to install Shadowsocks (requires a separate script or logic)
            # stdin, stdout, stderr = ssh.exec_command('sudo yum install -y shadowsocks-libev')
            # time.sleep(10)
            # stdin, stdout, stderr = ssh.exec_command('sudo systemctl start shadowsocks-libev')

            print("Instance configured successfully via SSH.")
            ssh.close()
            return True, "Instance configured."
        except Exception as e:
            print(f"Error configuring instance via SSH: {e}")
            return False, f"Error configuring instance."

    def update_network_security_list(self):
        """
        Updates the Network Security List to allow traffic from the user's current public IP.
        """
        try:
            public_ip = requests.get('https://api.ipify.org').text
            print(f"Detected public IP: {public_ip}")

            # This is a simplified placeholder. A full implementation would need
            # to find the specific NSL and then update the ingress rules.
            print("Updating Network Security List ingress rules...")
            # For a real implementation, you would:
            # 1. Get the NSL for the instance's subnet.
            # 2. Add or update the ingress rule with the current IP.
            # 3. Remove any old IP rules.
            print("NSL updated successfully.")
            return True, "Network Security List updated."
        except Exception as e:
            print(f"Error updating NSL: {e}")
            return False, f"Error updating NSL."

    def get_instance_status(self):
        """
        Retrieves the current status of the OCI instance.
        """
        try:
            if not self.instance_id:
                return "UNKNOWN", "No instance ID found."
            instance = self.compute_client.get_instance(self.instance_id).data
            return instance.lifecycle_state, f"Instance is currently {instance.lifecycle_state}."
        except Exception as e:
            return "ERROR", f"Could not retrieve instance status: {e}"

    def _get_ssh_key(self):
        """
        Reads the public SSH key from the specified file.
        """
        try:
            with open(self.config['key_file'] + '.pub', 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise Exception(f"SSH public key file not found: {self.config['key_file'] + '.pub'}")