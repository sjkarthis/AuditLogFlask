from confluent_kafka import Producer, KafkaException
import json
import configparser

# Load configuration from properties file
config = configparser.ConfigParser()
config.read('/config/config.properties')

# Get Kafka bootstrap servers from the configuration
KAFKA_BOOTSTRAP_SERVERS = config.get('DEFAULT', 'kafka.bootstrap.servers', fallback='localhost:9092')

# Kafka producer configuration
kafka_config = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'client.id': 'rest-service-producer',
}

producer = Producer(kafka_config)

def publish_to_kafka(topic, message):
    def delivery_report(err, msg):
        if err is not None:
            print(f'Message delivery failed: {err}')
            # Implement circuit breaker logic here if needed
        else:
            print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    producer.produce(topic, message.encode('utf-8'), callback=delivery_report)
    producer.flush()

def send_to_kafka(topic, data):
    try:
        # Convert data to JSON string (assuming data is a dictionary)
        message = json.dumps(data)
        publish_to_kafka(topic, message)
    except KafkaException as e:
        print(f'Failed to send message to Kafka: {e}')
        raise