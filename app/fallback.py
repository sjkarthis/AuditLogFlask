import json
import os

# Directory for local storage
LOCAL_STORAGE_DIR = 'local_storage/'

def store_locally(data):
    # Ensure local storage directory exists
    if not os.path.exists(LOCAL_STORAGE_DIR):
        os.makedirs(LOCAL_STORAGE_DIR)

    # Write data to a local file
    filename = f'{LOCAL_STORAGE_DIR}local_storage.txt'
    with open(filename, 'a') as f:
        json.dump(data, f)
        f.write('\n')
