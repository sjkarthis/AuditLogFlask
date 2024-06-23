from flask import Flask, request, jsonify

#from app.producer import send_to_kafka
#from app.fallback import store_locally

app = Flask(__name__)


# Example endpoint to create an object
@app.route('/create_object', methods=['POST'])
def create_object():
    # Extract input parameter from request body
    data = request.json
    object_name = data.get('object_name')

    if not object_name:
        return jsonify({'error': 'Missing object_name parameter'}), 400

    # Get user id from single sign-on headers (assuming it's in 'user_id' header)
    user_id = request.headers.get('user_id')

    try:
        # Publish to Kafka
        #send_to_kafka('my-topic', {'object_name': object_name, 'user_id': user_id})
        return jsonify({'message': f'Object {object_name} created for user {user_id}'}), 200
    except Exception as e:
        # Handle Kafka failure
        # Store information in local storage as fallback
        print(f'Failed to publish to Kafka: {e}')
        #store_locally({'object_name': object_name, 'user_id': user_id})
        return jsonify({'error': 'Failed to publish to Kafka, storing locally'}), 503


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
