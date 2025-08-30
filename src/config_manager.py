# config_manager.py
#
# This module provides a simple class for reading and validating the
# application's YAML configuration file.

import yaml

class ConfigParser:
    """
    Parses and validates the main application configuration file.
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def load_config(self):
        """
        Loads and returns the configuration from the YAML file.
        Also performs basic validation.
        
        Raises:
            FileNotFoundError: If the configuration file does not exist.
            yaml.YAMLError: If the YAML file is malformed.
            ValueError: If a required configuration field is missing.
        """
        try:
            with open(self.file_path, 'r') as file:
                config = yaml.safe_load(file)
            
            # Simple validation to ensure required top-level keys exist
            required_keys = ['oci', 'compute', 'shadowsocks', 'monitoring', 'routing']
            if not all(key in config for key in required_keys):
                raise ValueError("Missing one or more required top-level configuration keys.")
            
            return config
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found at: {self.file_path}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file: {e}")