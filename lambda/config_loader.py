import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def load_config(env="stage"):
    """
    Load the configuration file based on the environment.

    Args:
        env (str): The environment to load ('stage', 'prod').

    Returns:
        dict: The configuration as a dictionary.
    """
    config_folder = "config"
    config_file = os.path.join(config_folder, f"config.{env}.json")
    logging.info(f"Loading configuration from {config_file}")

    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file '{config_file}' not found.")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON in '{config_file}': {e}")
        raise
