# fallback.py

import json
import os

# Local storage configuration
LOCAL_STORAGE_PATH = os.getenv('LOCAL_STORAGE_PATH', '../local_storage/fallback_data.json')


def save_to_local_storage(data):
    """
    Saves data to local storage.

    Args:
        data (dict): The data to be saved.

    Raises:
        IOError: If there is an issue with writing to the local storage.
    """
    try:
        with open(LOCAL_STORAGE_PATH, 'a') as f:
            f.write(json.dumps(data) + '\n')
    except IOError as e:
        raise e
