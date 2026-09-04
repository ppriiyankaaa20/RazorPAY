from sqlalchemy import Column, Integer, String, Float
from database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(
        String,
        unique=True,
        index=True
    )

    country = Column(String)

    currency = Column(String)

    amount = Column(Float)

    payment_type = Column(String)

    attempt = Column(Integer, default=1)

    status = Column(String)

    error_code = Column(
        String,
        nullable=True
    )

    authentication_required = Column(
        Integer,
        default=0
    )

    retry_count = Column(
        Integer,
        default=0
    )

    recovered = Column(
        Integer,
        default=0
    )