# local_client_manager.py
#
# This module provides the core functionality for managing the local Shadowsocks
# client on the user's machine, particularly for macOS. It handles starting, stopping,
# and configuring the client, as well as generating connection details and
# testing connectivity.
#
# The module is designed to be integrated with the main application controller,
# which will provide the necessary configuration data from the user and the OCI Manager.

import subprocess
import os
import json
import yaml
import base64
import sys

# Optional external dependencies, assumed to be installed (e.g., via pip)
try:
    import qrcode
    import requests
except ImportError:
    print("Warning: Missing dependencies. `qrcode` and `requests` are required for full functionality.")
    # Exit if we can't import the libraries.
    sys.exit(1)


class LocalClientManager:
    """
    Manages the local Shadowsocks client, handling its lifecycle and configuration.
    """

    def __init__(self, config):
        """
        Initializes the manager with client configuration.

        Args:
            config (dict): A dictionary containing client configuration, including
                           'server_ip', 'server_port', 'local_port', 'password', and 'method'.
        """
        self.config = config
        self.client_process = None
        # Path for a temporary configuration file to be passed to ss-local
        self.client_config_path = "ss-local-temp.json"
        
        # Determine the name of the shadowsocks client executable based on the OS.
        # This assumes the user has installed the client via a package manager like Homebrew.
        if sys.platform == "darwin":  # macOS
            self.client_executable = "ss-local"
        else:
            # Add other operating systems and their client executables here
            self.client_executable = "ss-local" # Default for Linux/Windows


    def generate_connection_details(self):
        """
        Generates a Shadowsocks URL and QR code for easy mobile setup.

        Returns:
            tuple: A tuple containing the ss:// URL and the path to the saved QR code image.
        """
        # Create a dictionary of connection details for the URL.
        details = {
            "server": self.config['server_ip'],
            "server_port": self.config['server_port'],
            "password": self.config['password'],
            "method": self.config['method']
        }
        
        # Shadowsocks URL format is ss://base64(method:password@server:port)
        # Note: The original format is base64(method:password@server:port)
        # However, the more common format for client apps is base64(json_object)
        # This implementation uses a JSON payload for broader client compatibility.
        json_payload = json.dumps(details).encode('utf-8')
        encoded_payload = base64.b64encode(json_payload).decode('utf-8')
        ss_url = f"ss://{encoded_payload}"
        
        # Generate and save the QR code image.
        img = qrcode.make(ss_url)
        qr_filename = "shadowsocks_qrcode.png"
        img.save(qr_filename)
        
        return ss_url, qr_filename

    def test_connection(self, url):
        """
        Tests the proxy connection by making a request through the local client.

        Args:
            url (str): The URL to test the connection against.

        Returns:
            tuple: A tuple (bool, str) indicating success and a status message.
        """
        # Configure the request to use the local SOCKS proxy.
        proxies = {
            'http': f'socks5h://127.0.0.1:{self.config["local_port"]}',
            'https': f'socks5h://127.0.0.1:{self.config["local_port"]}'
        }
        
        try:
            response = requests.get(url, proxies=proxies, timeout=10)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            return True, "Connection successful."
        except requests.exceptions.RequestException as e:
            return False, f"Connection failed: {e}"

