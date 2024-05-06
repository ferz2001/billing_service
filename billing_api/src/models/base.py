import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Column, DateTime, String, Float, Integer, \
    ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base: Any = declarative_base()


@dataclass
class PaymentStatus:
    pending = 'pending'
    success = 'succeeded'


class UUidMixin(object):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)


class Subscriptions(UUidMixin, Base):
    __tablename__ = 'subscriptions'

    title = Column(String(255), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    duration = Column(Integer,
                      nullable=False)  # Длительность подписки в месяцах

    Payments = relationship("Payments", back_populates='Subscription')
    UserSubscriptions = relationship("UserSubscriptions", back_populates='Subscription')

    def __str__(self):
        return self.title


class Payments(UUidMixin, Base):
    __tablename__ = 'payments'

    service_payment_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    subscription_id = Column(ForeignKey('subscriptions.id'), nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(String(255), nullable=False)
    date_create = Column(DateTime(timezone=True), server_default=func.now(),
                         nullable=False, index=True)

    Subscription = relationship("Subscriptions", back_populates='Payments')
    UserSubscriptions = relationship("UserSubscriptions", back_populates='Payment')

    def __str__(self):
        return str(self.id)


class UserSubscriptions(UUidMixin, Base):
    __tablename__ = 'user_subscriptions'

    user_id = Column(UUID(as_uuid=True), nullable=False)
    subscription_id = Column(ForeignKey('subscriptions.id'), nullable=False)
    payment_id = Column(ForeignKey('payments.id'), nullable=False)
    is_active = Column(Boolean)
    expiration_time = Column(DateTime(timezone=True), nullable=False)
    auto_prolongate = Column(Boolean, nullable=False, default=False)
    Subscription = relationship("Subscriptions", back_populates='UserSubscriptions')
    Payment = relationship("Payments", back_populates='UserSubscriptions')
