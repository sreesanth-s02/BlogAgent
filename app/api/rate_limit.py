import time
from fastapi import HTTPException, Request

RATE_LIMITS = {}

def rate_limit(key: str, limit: int, window: int):
    def dependency(request: Request):
        ip = request.client.host
        now = time.time()

        bucket = RATE_LIMITS.setdefault((ip, key), [])
        bucket[:] = [t for t in bucket if now - t < window]

        if len(bucket) >= limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        bucket.append(now)

    return dependency
