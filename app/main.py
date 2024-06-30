# main.py
import re
from datetime import datetime
from json import dumps

from flask import Flask, request, jsonify
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.propagate import extract

from app.getlogs import get_logs
from producer import produce_message
from healthcheck import health_check
from fallback import save_to_local_storage
import os
from shared_utils import load_config, setup_logging, get_logger, get_config_value
from shared_utils.opentelemetry_setup import setup_opentelemetry

# Setup open telemetry
setup_opentelemetry()

RequestsInstrumentor().instrument()

# Load the configuration
load_config()

# Initialize Flask app
app = Flask(__name__)

# Setup logger
setup_logging()
logger = get_logger(__name__)
tracer = trace.get_tracer(__name__)

per_page = int(get_config_value('DEFAULT', 'per_page'))


@app.before_request
def start_span():
    context = extract(request.headers)
    request.span = tracer.start_span(name=request.path, context=context)


@app.after_request
def end_span(response):
    request.span.end()
    response.headers['X-Trace-ID'] = str(request.span.get_span_context().trace_id)
    return response


def is_valid(variable):
    return variable is not None and variable != '' and bool(variable)


def is_valid_user_id(user_id):
    # Example validation: Ensure user_id is alphanumeric and of a certain length
    if re.match(r'^[a-zA-Z0-9_-]{5,50}$', user_id):
        return True
    else:
        return False


def validate_request(data, headers):
    # Validate object name
    object_name = data.get('object_name')
    if not is_valid(object_name):
        return jsonify({"error": "Object name is required."}), 400

    # Validate user ID from headers
    user_id = headers.get('X-User-ID')
    if not is_valid_user_id(user_id):
        return jsonify({"error": "User not authorized."}), 401

    return None


# Function to validate and parse start_after_date
def validate_and_parse_date(date_str):
    try:
        # Parse the date string to a datetime object
        parsed_date = datetime.fromisoformat(date_str)
        return parsed_date
    except ValueError:
        # If parsing fails, return None
        return None


@app.route('/health', methods=['GET'])
def health_check_api():
    return jsonify({'status': health_check()})


@app.route('/auditlog/v1/create_object', methods=['POST'])
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
        'object_name': object_name
    }

    try:
        # Publish to Kafka with circuit breaker and key
        logger.info("Publish message to Kafka")
        produce_message(user_id, message)
    except Exception as e:
        # Save to local storage on any exception
        save_to_local_storage(message)
        logger.error(f"Failed to publish to Kafka: {e}. Data saved locally.")

    logger.info("Object created successfully!")
    return jsonify({"message": "Object created successfully"}), 201


# Endpoint to get audit logs for a specific user with pagination
@app.route('/audit_logs', methods=['GET'])
def get_audit_logs():
    """
    Endpoint to get audit logs.
    Expects a header 'X-User-ID'.
    """
    try:
        # Extract user_id from X-User-ID header
        user_id = request.headers.get('X-User-ID')

        # Validate user_id to avoid SQL injection
        if not is_valid_user_id(user_id):
            return jsonify({'status': 'error', 'message': 'Invalid X-User-ID format'}), 400

        # Pagination parameters
        page_number = int(request.args.get('page', 1))  # Default page number is 1
        if page_number < 1:
            page_number = 1
        page_size = int(request.args.get('page_size', 10))  # Default page size is 10
        if page_size > per_page:  # Limit maximum page size to 100 for practical reasons
            page_size = per_page

        audit_logs_list = get_logs(page_number, page_size, user_id)

        # Determine if there's a next page
        next_page_number = page_number + 1 if len(audit_logs_list) == page_size else None

        # Return paginated audit logs and next page number as JSON response
        return jsonify({
            'status': 'success',
            'data': audit_logs_list,
            'page_number': page_number,
            'page_size': page_size,
            'next_page': next_page_number
        }), 200

    except Exception as e:
        logger.error(f"Failed to get audit logs : {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    # Run Flask app
    FlaskInstrumentor().instrument_app(app)
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
