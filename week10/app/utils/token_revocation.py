import logging

import pybreaker

from app.extensions import redis_client


logger = logging.getLogger(__name__)

token_revocation_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=15,
    name="token_revocation_redis",
)


def _jti_preview(jti):
    return f"{jti[:8]}..." if jti else None


def token_revocation_breaker_status():
    return {
        "name": token_revocation_breaker.name,
        "state": token_revocation_breaker.current_state,
        "failure_count": token_revocation_breaker.fail_counter,
        "failure_threshold": token_revocation_breaker.fail_max,
        "recovery_timeout": token_revocation_breaker.reset_timeout,
    }


def is_token_revoked(jti):
    logger.debug("checking token revocation", extra={"jti": _jti_preview(jti)})
    return token_revocation_breaker.call(
        redis_client.get,
        f"revoked_token:{jti}",
    )


def revoke_token_jti(jti, ttl_seconds):
    if ttl_seconds <= 0:
        logger.info(
            "skip revoking expired token",
            extra={"jti": _jti_preview(jti), "ttl_seconds": ttl_seconds},
        )
        return None

    logger.info("revoking token", extra={"jti": _jti_preview(jti), "ttl_seconds": ttl_seconds})
    return token_revocation_breaker.call(
        redis_client.setex,
        f"revoked_token:{jti}",
        ttl_seconds,
        "true",
    )
