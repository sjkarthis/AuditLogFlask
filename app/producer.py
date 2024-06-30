from opentelemetry.instrumentation.requests import RequestsInstrumentor

from shared_utils import get_logger, get_config_value
from kafka import KafkaProducer
from kafka.errors import KafkaError
import pybreaker
import json
from opentelemetry.instrumentation.kafka import KafkaInstrumentor

KafkaInstrumentor().instrument()

logger = get_logger(__name__)

# Kafka configuration
KAFKA_BROKER = get_config_value('DEFAULT', 'kafka.bootstrap.servers')
TOPIC_NAME = get_config_value('DEFAULT', 'kafka.topic.service.replay')

try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        security_protocol='PLAINTEXT'
    )
except Exception as e:
    logger.info(f"Unable to initialize Kafka producer: {e}")

# Circuit breaker configuration
circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=get_config_value('DEFAULT', 'circuit.breaker.failMax'),
    reset_timeout=get_config_value('DEFAULT', 'circuit.breaker.reset.timeout.seconds')
)


def send_message(key, message):
    try:
        logger.info(f"Sending KAFKA message '{message}' with key '{key}' to topic '{TOPIC_NAME}'")
        future = producer.send(TOPIC_NAME, key=key.encode(), value=message)
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
        send_message(key, message)
    except Exception as e:
        logger.error(f"Error in producing message: {e}")
        raise
