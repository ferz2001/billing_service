import uuid
from typing import Any

from fastapi import APIRouter, Depends, Body, HTTPException
from yookassa.domain.notification import WebhookNotificationFactory

from core.config import settings
from services.auth import get_current_user_data
from services.billing import get_billing_service, BillingService

router = APIRouter()


@router.post(
    '/create',
    summary="Создать платеж",
    description="Возвращает ссылку на оплату платежа"
)
async def create_payment(
        subscribe_id: uuid.UUID,
        user_payload: dict = Depends(get_current_user_data),
        billing_service: BillingService = Depends(get_billing_service)
):
    user_id = uuid.UUID(user_payload['user_id'])
    user_email = user_payload['email']
    return_url = settings.return_url
    return await billing_service.create_new_payment(
        user_id,
        user_email,
        subscribe_id,
        return_url,
    )


@router.post(
    '/notify',
    summary="Принимаем сообщение от юкассы",
    description=""
)
async def notify(
        event_json: Any = Body(None),
        billing_service: BillingService = Depends(get_billing_service)
):  # Извлечение JSON объекта из тела запроса
    notification_object = WebhookNotificationFactory().create(event_json)
    response_object = notification_object.object
    yookassa_payment_id = response_object.id
    new_status = response_object.status
    # try:
    await billing_service.update_payment_status(yookassa_payment_id,
                                                new_status)
    # except Exception as err:
    #     print(err)
    #     return HTTPException(400)
    return HTTPException(200)  # Сообщаем кассе, что все хорошо


@router.post(
    '/auto_prolongate'
)
async def auto_prolongate(
        user_subscription_id: uuid.UUID,
        user_payload: dict = Depends(get_current_user_data),
        billing_service: BillingService = Depends(get_billing_service)
):
    user_id = uuid.UUID(user_payload['user_id'])
    await billing_service.prolongate_subscribe(user_id, user_subscription_id)
