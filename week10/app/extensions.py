from flask_sqlalchemy import SQLAlchemy
import redis

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics.for_app_factory(path=None)

db = SQLAlchemy() 
redis_client = redis.from_url("redis://localhost:6379/0")


limiter = Limiter(
    get_remote_address, 
    default_limits=["10 per minute", "100 per hour"]
)
