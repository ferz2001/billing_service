import datetime
import logging
import uuid
from datetime import timedelta

from fastapi import Depends, HTTPException, status
from yookassa import Configuration, Payment

from core.config import settings
from db.postgres import DbService, get_session
from models.base import Subscriptions, Payments, PaymentStatus, \
    UserSubscriptions

logger = logging.getLogger('billing_api')

Configuration.configure(
    settings.yookassa_shop_id,
    settings.yookassa_secret_key
)


class BillingService:
    def __init__(self, db: DbService):
        self.db = db

    async def _get_pending_payment(self,
                                   service_payment_id: uuid.UUID,
                                   payment_status: str) -> Payments:
        """
        status: pending, succeeded
        """
        payments_data = await self.db.select(
            Payments,
            [
                (Payments.service_payment_id, service_payment_id),
                (Payments.status, payment_status)
            ]
        )
        return payments_data[0]

    async def _get_user_subscribe(
            self,
            user_subscription_id: uuid.UUID,
    ) -> UserSubscriptions:
        user_subscribe_data = await self.db.select(
            UserSubscriptions,
            [
                (UserSubscriptions.id, user_subscription_id),
            ]
        )
        if not user_subscribe_data:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                'user_subscribe not exist')
        return user_subscribe_data[0]

    async def _create_db_new_payment(
            self,
            user_id: uuid.UUID,
            subscription_id: uuid.UUID,
            yookassa_payment_id: uuid.UUID,
            price: int,
            payment_status: PaymentStatus = PaymentStatus.pending
    ) -> Payments:
        return await self.db.insert(
            Payments,
            {
                'service_payment_id': yookassa_payment_id,
                "user_id": user_id,
                'subscription_id': subscription_id,
                'price': price,
                'status': payment_status,
                'date_create': datetime.datetime.now()
            }
        )

    async def _get_subscription(
            self,
            subscription_id: uuid.UUID
    ) -> Subscriptions:
        try:
            subscription_data = await self.db.select(
                Subscriptions,
                where_select=[(Subscriptions.id, subscription_id)]
            )
            return subscription_data[0]
        except Exception:
            raise HTTPException(404, 'Подписка с таким id не существует')

    async def _increase_user_subscribe_time(self, subscription_id: uuid.UUID,
                                            user_id: uuid.UUID,
                                            payment_id: uuid.UUID):
        """
        Создает пользовательскую подписку или продлевает ее
        """
        subscription = await self._get_subscription(subscription_id)
        user_subscribe_data = await self.db.select(
            UserSubscriptions,
            [
                (UserSubscriptions.user_id, user_id),
                (UserSubscriptions.subscription_id, subscription_id)
            ]
        )
        if not user_subscribe_data:
            user_subscribe = await self.db.insert(
                UserSubscriptions,
                {
                    'user_id': user_id,
                    'subscription_id': subscription_id,
                    'payment_id': payment_id,
                    'is_active': True,
                    'expiration_time': datetime.datetime.now() + timedelta(
                        subscription.duration * 30),
                    'auto_prolongate': True
                }
            )
        else:
            user_subscribe: UserSubscriptions = user_subscribe_data[0]
            user_expiration_time = user_subscribe.expiration_time
            if user_expiration_time < datetime.datetime.utcnow().replace(
                    tzinfo=datetime.timezone.utc):
                user_expiration_time = datetime.datetime.utcnow().replace(
                    tzinfo=datetime.timezone.utc)

            await self.db.update(
                UserSubscriptions,
                {
                    'payment_id': payment_id,
                    'is_active': True,
                    'expiration_time': user_expiration_time + timedelta(
                        subscription.duration * 30),
                },
                [UserSubscriptions.id, user_subscribe.id]
            )

    async def prolongate_subscribe(self, user_id: uuid.UUID,
                                   user_subscription_id: uuid.UUID) -> bool:
        """
        Продлевает подписку по последнему платежу
        Возвращает True если получилось
        """
        user_subscribe = await self._get_user_subscribe(user_subscription_id)
        if not user_subscribe.auto_prolongate:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                'Subscribtion not autoprolongate')

        subscription = await self._get_subscription(
            user_subscribe.subscription_id)
        last_payment_data = await self.db.select(Payments, [
            (Payments.id, user_subscribe.payment_id)])
        last_payment: Payments = last_payment_data[0]

        yookassa_payment = Payment.create({
            "amount": {
                "value": f"{subscription.price}",
                "currency": "RUB"
            },
            "capture": True,
            "payment_method_id": f"{last_payment.service_payment_id}",
            "description": f"{subscription.title}"
        })

        payment = await self._create_db_new_payment(
            user_id, subscription.id, last_payment.service_payment_id,
            subscription.price, yookassa_payment.status
        )
        if yookassa_payment.status == "succeeded":
            await self._increase_user_subscribe_time(
                subscription_id=payment.subscription_id,
                user_id=payment.user_id,
                payment_id=payment.id
            )
            return True
        return False

    async def create_new_payment(
            self,
            user_id: uuid.UUID,
            user_email: str,  # для отправки чека
            subscription_id: uuid.UUID,
            return_url: str,
    ) -> str:
        """
        Создает платеж в БД и возвращает ссылку на оплату.
        """
        subscription = await self._get_subscription(subscription_id)
        yookassa_payment = Payment.create({
            "description": f"Подписка  {subscription.title}",
            "amount": {
                "value": subscription.price,
                "currency": "RUB"
            },
            "receipt": {
                "customer": {
                    "email": user_email
                },
                "items": [
                    {
                        "description": f"Подписка  {subscription.title}",
                        "quantity": "1",
                        "amount": {
                            "value": subscription.price,
                            "currency": "RUB"
                        },
                        "vat_code": "1"
                    },
                ],
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "save_payment_method": True
        }, uuid.uuid4())

        await self._create_db_new_payment(
            user_id,
            subscription_id,
            yookassa_payment.id,
            subscription.price
        )

        return yookassa_payment.confirmation.confirmation_url

    async def update_payment_status(self, yookassa_payment_id: uuid.UUID,
                                    new_status: str):
        """
        Обновляет статус платежа в бд и продлевает подписку в случае успеха
        """
        try:
            payment = await self._get_pending_payment(yookassa_payment_id,
                                                      "pending")
        except Exception:
            return

        if payment.status == "succeeded":
            return

        await self.db.update(Payments, {'status': new_status},
                             [Payments.id, payment.id])

        if new_status == "succeeded":
            await self._increase_user_subscribe_time(
                subscription_id=payment.subscription_id,
                user_id=payment.user_id,
                payment_id=payment.id
            )


def get_billing_service(
        session=Depends(get_session)) -> BillingService:
    db = DbService(db=session)
    return BillingService(db=db)
