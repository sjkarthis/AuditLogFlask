from datetime import datetime

from bson.json_util import dumps
from flask import request
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor

from shared_utils import connect_to_db, get_config_value, setup_logging, get_logger

# Setup logger
setup_logging()
logger = get_logger(__name__)

PymongoInstrumentor().instrument()

collection, client = connect_to_db(get_config_value('DEFAULT', 'mongo.uri'),
                                   get_config_value('DEFAULT', 'mongo.db_name'),
                                   get_config_value('DEFAULT', 'mongo.collection_name'),
                                   get_config_value('DEFAULT', 'mongo.max_pool_size'),
                                   get_config_value('DEFAULT', 'mongo.socket_timeout_ms'))


def get_logs(page_number, page_size, user_id):
    logger.info(f"Getting logs for user {user_id}, page {page_number}, page size {page_size}")
    # Calculate skip value based on page number and page size
    skip = (page_number - 1) * page_size
    # Query MongoDB for audit logs for the specified user_id, paginated by page number
    query = {'user_id': user_id}
    # Fetch audit logs with pagination
    audit_logs = collection.find(query, {'_id': 0}).skip(skip).limit(page_size)
    # Convert MongoDB cursor to JSON format
    audit_logs_list = list(audit_logs)
    return audit_logs_list
