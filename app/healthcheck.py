import requests
from kafka import KafkaAdminClient
from kafka.errors import KafkaError

from shared_utils import load_config, setup_logging, get_logger, get_config_value

# Load the configuration
load_config()

# Setup logger
setup_logging()
logger = get_logger(__name__)

consumer_app_healthcheck_url = get_config_value('DEFAULT', 'healthcheck.consumer.url')
external_system_healthcheck_url = get_config_value('DEFAULT', 'healthcheck.external_system.url')
KAFKA_BROKER = get_config_value('DEFAULT', 'kafka.bootstrap.servers')


def check_dependent_system(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return {'status': 'up', 'response': response.json().get('status')}
        else:
            return {'status': 'down', 'message': f"Dependency {url} returned status code {response.status_code}"}
    except requests.RequestException as e:
        return {'status': 'down', 'message': f"Dependency {url} error: {str(e)}"}


def check_kafka_status():
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BROKER)
        # Attempt to fetch broker metadata to verify connection
        metadata = admin_client.describe_cluster()
        if metadata:
            return {'status': 'up'}
        else:
            return {'status': 'down', 'message': 'No metadata returned'}
    except KafkaError as e:
        return {'status': 'down', 'message': f"Kafka error: {str(e)}"}
    except Exception as e:
        return {'status': 'down', 'message': f"General error: {str(e)}"}


def health_check():
    # Check dependent systems
    consumer_status = check_dependent_system(consumer_app_healthcheck_url)
    external_system_status = check_dependent_system(external_system_healthcheck_url)
    kafka_status = check_kafka_status()

    # Aggregate responses
    overall_status = 'up'
    if consumer_status['status'] == 'down' or external_system_status['status'] == 'down' or kafka_status['status'] == 'down':
        overall_status = 'down'

    # Log statuses
    logger.info(f"Audit log service consumer status: {consumer_status}")
    logger.info(f"External system status: {external_system_status}")
    logger.info(f"Kafka Status: {kafka_status}")
    logger.info(f"Overall Health Status: {overall_status}")

    # Return aggregated response
    response_data = {
        'overall_status': overall_status,
        'Consumer_status': consumer_status,
        'External_system_status': external_system_status,
        'kafka': kafka_status
    }

    return response_data
