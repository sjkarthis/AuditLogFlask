import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError
import pybreaker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_BROKER = 'localhost:9092'  # Adjust this to your broker address
TOPIC_NAME = 'my_topic'  # Adjust this to your topic name

# Initialize Kafka producer with authentication
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    security_protocol='SASL_PLAINTEXT',
    sasl_mechanism='PLAIN',
    sasl_plain_username='user1',
    sasl_plain_password='shw3O1zBZy',
    value_serializer=lambda v: v.encode('utf-8')
)

# Circuit breaker configuration
circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=5,  # Maximum number of failures before opening the circuit
    reset_timeout=30  # Time in seconds before attempting to close the circuit again
)


def send_message(key, message):
    """
    Function to send a message to Kafka with key
    """
    try:
        future = producer.send(TOPIC_NAME, key=key, value=message)
        result = future.get(timeout=10)  # Block for 'synchronous' sends
        logger.info(f"Message '{message}' with key '{key}' sent to topic '{topic}'")
        return result
    except KafkaError as e:
        logger.error(f"Failed to send message '{message}' with key '{key}': {e}")
        raise


@circuit_breaker
def produce_message(key, message):
    """
    Produces a message to Kafka with circuit breaker protection
    """
    try:
        send_message(key, message)
    except Exception as e:
        logger.error(f"Error in producing message: {e}")
        raise
