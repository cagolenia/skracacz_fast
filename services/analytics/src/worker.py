import asyncio
import aio_pika
import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from src.config import settings
from src.database import SessionLocal, init_db
from src.models import LinkVisit

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_user_agent(user_agent: str) -> str:
    """Prosta funkcja do określenia typu urządzenia z User-Agent"""
    if not user_agent:
        return "unknown"
    
    user_agent_lower = user_agent.lower()
    
    if "bot" in user_agent_lower or "spider" in user_agent_lower:
        return "bot"
    elif "mobile" in user_agent_lower or "android" in user_agent_lower:
        return "mobile"
    elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
        return "tablet"
    else:
        return "desktop"


async def process_visit_event(message: aio_pika.IncomingMessage, db: Session):
    """Przetwarzanie pojedynczego zdarzenia odwiedzin"""
    async with message.process():
        try:
            # Dekodowanie wiadomości
            event_data = json.loads(message.body.decode())
            
            logger.info(f"Processing visit event: {event_data.get('short_code')}")
            
            # Parsowanie danych
            timestamp_str = event_data.get("timestamp")
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            user_agent = event_data.get("user_agent", "")
            device_type = parse_user_agent(user_agent)
            
            # Zapis do bazy danych
            visit = LinkVisit(
                short_code=event_data.get("short_code"),
                timestamp=timestamp,
                ip_address=event_data.get("ip_address"),
                user_agent=user_agent,
                referer=event_data.get("referer"),
                device_type=device_type
            )
            
            db.add(visit)
            db.commit()
            
            logger.info(f"Saved visit for {visit.short_code}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")
        except Exception as e:
            logger.error(f"Failed to process visit event: {e}")
            db.rollback()


async def consume_messages():
    """Główna funkcja konsumenta RabbitMQ"""
    logger.info("Starting Analytics Worker...")
    
    # Inicjalizacja bazy danych
    init_db()
    logger.info("Database initialized")
    
    # Połączenie z RabbitMQ
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    channel = await connection.channel()
    
    # Ustawienie prefetch count
    await channel.set_qos(prefetch_count=settings.worker_prefetch_count)
    
    # Deklaracja kolejki
    queue = await channel.declare_queue(
        settings.rabbitmq_queue,
        durable=True
    )
    
    logger.info(f"Listening for messages on queue: {settings.rabbitmq_queue}")
    
    # Konsumpcja wiadomości
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            db = SessionLocal()
            try:
                await process_visit_event(message, db)
            finally:
                db.close()


def main():
    """Entry point dla workera"""
    try:
        asyncio.run(consume_messages())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker crashed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
