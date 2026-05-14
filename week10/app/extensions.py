from flask_sqlalchemy import SQLAlchemy

try:
    import redis
except ImportError:
    redis = None

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
redis_client = redis.from_url("redis://localhost:6379/0") if redis else None


limiter = Limiter(
    get_remote_address, 
    default_limits=["10 per minute", "100 per hour"]
)