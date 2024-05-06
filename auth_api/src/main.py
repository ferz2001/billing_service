import logging
from contextlib import asynccontextmanager

import asgi_correlation_id
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from starlette.middleware.sessions import SessionMiddleware
import sentry_sdk

from api.v1 import auth, roles, account, oauth
from core.config import settings
from core.jaeger import configure_tracer
from core.logger import LoggerSetup
from db import redis

logging_setup = LoggerSetup()
logger = logging.getLogger('auth_api')

if settings.sentry_dsn is not None:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        enable_tracing=True,
    )
    

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
    )
    await FastAPILimiter.init(redis.redis)
    
    yield
    await redis.redis.close()


dependencies = []
if settings.enable_rate_limiter:
    dependencies.append(
        Depends(
            RateLimiter(
                times=settings.rate_limiter_times,
                seconds=settings.rate_limiter_seconds,
            ),
        ),
    )

app = FastAPI(
    docs_url='/api/v1/auth/openapi',
    openapi_url='/api/v1/auth/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    dependencies=dependencies,
)

app.include_router(oauth.router, prefix='/api/v1/oauth')
app.include_router(auth.router, prefix='/api/v1/auth')
app.include_router(roles.router, prefix='/api/v1/roles')
app.include_router(account.router, prefix='/api/v1/account')

app.add_middleware(SessionMiddleware, secret_key=settings.session_secret_key)
app.add_middleware(asgi_correlation_id.CorrelationIdMiddleware)

if settings.enable_tracer:
    configure_tracer()
    FastAPIInstrumentor.instrument_app(app)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
    )
