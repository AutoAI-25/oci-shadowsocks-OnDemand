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

    # def start_client(self):
    #     """
    #     Starts the local Shadowsocks client as a subprocess.

    #     The method writes the client configuration to a temporary JSON file and
    #     then executes the `ss-local` command line utility.

    #     Returns:
    #         tuple: A tuple (bool, str) indicating success and a status message.
    #     """
    #     try:
    #         # Write a temporary client configuration file.
    #         client_details = {
    #             "server": self.config['server_ip'],
    #             "server_port": self.config['server_port'],
    #             "local_address": "127.0.0.1",
    #             "local_port": self.config['local_port'],
    #             "password": self.config['password'],
    #             "method": self.config['method']
    #         }
    #         with open(self.client_config_path, 'w') as f:
    #             json.dump(client_details, f, indent=4)
            
    #         # Start the client process in the background.
    #         self.client_process = subprocess.Popen(
    #             [self.client_executable, '-c', self.client_config_path],
    #             stdout=subprocess.PIPE,
    #             stderr=subprocess.PIPE
    #         )
    #         return True, "Client started successfully."

    #     except FileNotFoundError:
    #         return False, f"Error: '{self.client_executable}' not found. Please ensure it's in your PATH."
    #     except Exception as e:
    #         return False, f"Error starting client: {e}"

    # def stop_client(self):
    #     """
    #     Stops the running Shadowsocks client process.

    #     This method attempts to terminate the subprocess gracefully.

    #     Returns:
    #         tuple: A tuple (bool, str) indicating success and a status message.
    #     """
    #     if self.client_process and self.client_process.poll() is None:
    #         try:
    #             self.client_process.terminate()
    #             self.client_process.wait(timeout=5)  # Wait for the process to exit
    #             if os.path.exists(self.client_config_path):
    #                 os.remove(self.client_config_path)
    #             return True, "Client stopped successfully."
    #         except Exception as e:
    #             return False, f"Error stopping client: {e}"
    #     else:
    #         return False, "Client is not running."

    def generate_pac_file(self, rules_file, output_path):
        """
        Generates a Proxy Auto-Configuration (PAC) file based on routing rules.

        The PAC file will contain JavaScript logic to selectively route traffic
        based on the provided proxy domains.

        Args:
            rules_file (str): Path to the YAML file containing routing rules.
            output_path (str): The desired path to save the generated PAC file.

        Returns:
            bool: True if the file was generated successfully, False otherwise.
        """
        try:
            with open(rules_file, 'r') as f:
                rules = yaml.safe_load(f)
            
            proxy_domains = rules.get('proxy_domains', [])
            default_action = rules.get('default_action', 'DIRECT')
            
            pac_content = f"""
function FindProxyForURL(url, host) {{
    var proxy = "SOCKS5 127.0.0.1:{self.config['local_port']};";
    var direct = "DIRECT;";

    var proxy_domains = {json.dumps(proxy_domains)};

    for (var i = 0; i < proxy_domains.length; i++) {{
        if (shExpMatch(host, proxy_domains[i])) {{
            return proxy;
        }}
    }}
    return "{default_action}";
}}
"""
            with open(output_path, 'w') as f:
                f.write(pac_content)
            return True
        except Exception as e:
            print(f"Error generating PAC file: {e}")
            return False

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

