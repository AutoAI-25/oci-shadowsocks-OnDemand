# src/config_parser.py

import yaml
import os

class ConfigParser:
    """
    Manages the loading and parsing of the project's configuration file.
    """
    def __init__(self, config_path="config/settings.yaml"):
        """
        Initializes the parser with the path to the configuration file.

        Args:
            config_path (str): The path to the YAML configuration file.
        """
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        """
        Loads the configuration from the YAML file.

        Returns:
            tuple: A tuple (bool, str) indicating success and a status message.
        """
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            return True, "Config loaded successfully."
        except FileNotFoundError:
            return False, f"Error: Configuration file not found at {self.config_path}."
        except yaml.YAMLError as e:
            return False, f"Error parsing YAML file: {e}"