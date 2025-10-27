"""
RabbitMQ Configuration
Centralized settings for RabbitMQ connection and messaging
"""

# RabbitMQ Connection Settings
RABBITMQ_HOST = 'localhost'
RABBITMQ_PORT = 5672
RABBITMQ_USERNAME = 'guest'  # Default RabbitMQ username
RABBITMQ_PASSWORD = 'guest'  # Default RabbitMQ password
RABBITMQ_VIRTUAL_HOST = '/'

# Exchange Configuration
STREAMING_EXCHANGE_NAME = 'llm_streaming_exchange'
STREAMING_EXCHANGE_TYPE = 'topic'  # Using topic for routing by session_id

# Queue Configuration
def get_session_queue_name(session_id: str) -> str:
    """Generate queue name for a specific session"""
    return f"session_{session_id}"

# Routing Key Pattern
def get_routing_key(session_id: str, agent_name: str = None) -> str:
    """
    Generate routing key for message publishing
    Pattern: session.{session_id}.{agent_name}
    """
    if agent_name:
        return f"session.{session_id}.{agent_name}"
    return f"session.{session_id}.#"  # Wildcard for consuming all agent messages

# Message Types
class MessageType:
    LLM_CHUNK = "llm_chunk"
    FINAL_RESPONSE = "final_response"
    ERROR = "error"
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"

# Connection Parameters
CONNECTION_PARAMS = {
    'host': RABBITMQ_HOST,
    'port': RABBITMQ_PORT,
    'virtual_host': RABBITMQ_VIRTUAL_HOST,
    'credentials': {
        'username': RABBITMQ_USERNAME,
        'password': RABBITMQ_PASSWORD
    }
}

# Queue Settings
QUEUE_ARGUMENTS = {
    'x-message-ttl': 60000,  # Messages expire after 60 seconds
    'x-expires': 300000,     # Queue expires after 5 minutes of inactivity
}
