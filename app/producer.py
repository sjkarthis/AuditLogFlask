from logging_config import logger
from config import config
from kafka import KafkaProducer
from kafka.errors import KafkaError
import pybreaker
import json

# Kafka configuration
KAFKA_BROKER = config.get('DEFAULT', 'kafka.bootstrap.servers')
TOPIC_NAME = 'audit_log_service_replay'

# Initialize Kafka producer with authentication
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Circuit breaker configuration
circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30  # Time in seconds before attempting to close the circuit again
)


def send_message(key, message):
    """
    Function to send a message to Kafka with key
    """
    try:
        logger.info(f"Sending KAFKA message '{message}' with key '{key}' to topic '{TOPIC_NAME}'")
        future = producer.send(TOPIC_NAME, value=message)
        result = future.get(timeout=50)  # Block for 'synchronous' sends
        logger.info(f"Message '{message}' with key '{key}' sent to topic '{TOPIC_NAME}'")
        return result
    except KafkaError as e:
        logger.error(f"Failed to send message '{message}' with key '{key}': {e}")
        raise


@circuit_breaker
def produce_message(key, message):
    """
    Produces a message to Kafka with circuit breaker.
    """
    try:
        logger.info("Start publish ..")
        send_message(key, message)
    except Exception as e:
        logger.error(f"Error in producing message: {e}")
        raise
