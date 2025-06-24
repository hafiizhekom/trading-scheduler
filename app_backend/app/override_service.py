from app.models import PriceOverrideRequest
from app.db import insert_override_to_db
from app.redis_publisher import publish_override_to_redis

async def handle_override(payload: PriceOverrideRequest):
    insert_override_to_db(payload)
    await publish_override_to_redis(payload)
