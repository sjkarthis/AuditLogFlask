# main.py

from flask import Flask, request, jsonify
from producer import produce_message
from fallback import save_to_local_storage
import json
import os
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Local storage configuration
LOCAL_STORAGE_PATH = os.getenv('LOCAL_STORAGE_PATH', '../local_storage/fallback_data.json')


def is_valid(variable):
    """
    Checks if a variable is not None, not an empty string, and not a falsy value.
    """
    return variable is not None and variable != '' and bool(variable)


def validate_request(data, headers):
    """
    Validates the request data and headers.

    Args:
        data (dict): The JSON payload from the request.
        headers (Headers): The headers from the request.

    Returns:
        tuple: A tuple containing a boolean indicating validity, and an error response or None.
    """
    # Validate object name
    object_name = data.get('object_name')
    if not is_valid(object_name):
        return jsonify({"error": "Object name is required."}), 400

    # Validate user ID from headers
    user_id = headers.get('X-User-ID')
    if not is_valid(user_id):
        return jsonify({"error": "User ID is required."}), 401

    return None


@app.route('/create_object', methods=['POST'])
def create_object():
    """
    Endpoint to create an object.
    Expects a JSON payload with 'name' and a header 'X-User-ID'.
    Publishes the data to Kafka or saves to local storage if Kafka is unavailable.
    """
    data = request.get_json()
    headers = request.headers

    # Validate the request
    error_response = validate_request(data, headers)
    if error_response:
        logger.warning("Validation error: %s", error_response)
        return error_response

    object_name = data.get('object_name')
    user_id = headers.get('X-User-ID')

    # Create message
    message = {
        'user_id': user_id,
        'object_name': object_name
    }

    try:
        # Publish to Kafka with circuit breaker and key
        produce_message(user_id, message)
    except Exception as e:
        # Save to local storage on any exception
        save_to_local_storage(message)
        logger.error(f"Failed to publish to Kafka: {e}. Data saved locally.")

    logger.info("Object created successfully")
    return jsonify({"message": "Object created successfully"}), 201


if __name__ == '__main__':
    # Create local storage file if it doesn't exist
    if not os.path.exists(LOCAL_STORAGE_PATH):
        with open(LOCAL_STORAGE_PATH, 'w') as f:
            pass

    # Run Flask app
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 6000)))