import pybreaker

from app.extensions import redis_client


token_revocation_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=15,
    name="token_revocation_redis",
)


def token_revocation_breaker_status():
    return {
        "name": token_revocation_breaker.name,
        "state": token_revocation_breaker.current_state,
        "failure_count": token_revocation_breaker.fail_counter,
        "failure_threshold": token_revocation_breaker.fail_max,
        "recovery_timeout": token_revocation_breaker.reset_timeout,
    }


def is_token_revoked(jti):
    return token_revocation_breaker.call(
        redis_client.get,
        f"revoked_token:{jti}",
    )


def revoke_token_jti(jti, ttl_seconds):
    if ttl_seconds <= 0:
        return None

    return token_revocation_breaker.call(
        redis_client.setex,
        f"revoked_token:{jti}",
        ttl_seconds,
        "true",
    )
