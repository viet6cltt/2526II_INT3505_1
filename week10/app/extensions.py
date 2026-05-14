from flask_sqlalchemy import SQLAlchemy
import redis

db = SQLAlchemy() 
redis_client = redis.from_url("redis://localhost:6379/0")