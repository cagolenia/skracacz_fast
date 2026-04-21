import aio_pika
import json
import logging
from src.config import settings

logger = logging.getLogger(__name__)


class MessageQueue:
    """RabbitMQ connection manager"""
    
    _instance = None
    _connection = None
    _channel = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Establish connection to RabbitMQ"""
        if self._connection is None or self._connection.is_closed:
            try:
                self._connection = await aio_pika.connect_robust(settings.rabbitmq_url)
                self._channel = await self._connection.channel()
                
                # Deklaracja kolejki
                await self._channel.declare_queue(
                    settings.rabbitmq_queue,
                    durable=True
                )
                logger.info("Connected to RabbitMQ")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise
    
    async def disconnect(self):
        """Close RabbitMQ connection"""
        if self._channel:
            await self._channel.close()
        if self._connection:
            await self._connection.close()
        self._connection = None
        self._channel = None
        logger.info("Disconnected from RabbitMQ")
    
    async def publish_event(self, event_data: dict):
        """Publish event to queue"""
        if not self._channel:
            await self.connect()
        
        try:
            message = aio_pika.Message(
                body=json.dumps(event_data).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            
            await self._channel.default_exchange.publish(
                message,
                routing_key=settings.rabbitmq_queue
            )
            logger.debug(f"Published event: {event_data}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")


# Global queue instance
message_queue = MessageQueue()
