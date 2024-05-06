import logging
from contextlib import asynccontextmanager

import asgi_correlation_id
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from admin import SubscriptionAdmin, PaymentsAdmin, UserSubscriptionsAdmin, \
    AdminAuth
from api.v1 import billing
from core.config import settings
from core.logger import LoggerSetup
from db import redis
from db.postgres import engine

logging_setup = LoggerSetup()
logger = logging.getLogger('billing_api')


@asynccontextmanager
async def lifespan(*args, **kwargs):
    logger.info('Billing API service started')
    redis.redis = Redis(
        host=settings.redis_host,
        port=settings.redis_port
    )
    yield
    logger.info('Billing API service stopped')
    

app = FastAPI(
    lifespan=lifespan,
    title=settings.app_name,
    docs_url='/api/v1/billing/openapi',
    openapi_url='/api/v1/billing/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

admin = Admin(
    app, engine,
    base_url='/api/v1/billing/admin',
    title='Billing admin panel',
    authentication_backend=AdminAuth(secret_key=settings.jwt_secret_key)
)
admin.add_view(SubscriptionAdmin)
admin.add_view(PaymentsAdmin)
admin.add_view(UserSubscriptionsAdmin)

app.include_router(billing.router, prefix='/api/v1/billing', tags=['billing'])

app.add_middleware(asgi_correlation_id.CorrelationIdMiddleware)
app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret_key)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8002,
        reload=True,
    )
