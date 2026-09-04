from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI(
    title="Smart Global Retry Agent",
    version="1.0.0",
    description="AI-powered international payment failure analysis system"
)


# --------------------------------------------------
# CORS CONFIGURATION
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# PAYMENT REQUEST MODEL
# --------------------------------------------------

class PaymentRequest(BaseModel):
    amount: float
    country: str
    failure_reason: str
    three_ds_supported: bool


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Smart Global Retry Agent is running!"
    }


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# --------------------------------------------------
# PAYMENT ANALYSIS
# --------------------------------------------------

@app.post("/payment/analyze")
def analyze_payment(payment: PaymentRequest):

    reason = payment.failure_reason.upper()

    # 1. 3DS authentication required
    if reason == "3DS_REQUIRED":
        return {
            "amount": payment.amount,
            "country": payment.country,
            "failure_reason": reason,
            "recommended_action": "3DS_REQUIRED",
            "message": "Payment needs 3DS authentication."
        }

    # 2. Temporary technical failure
    elif reason == "TECHNICAL_ERROR":
        return {
            "amount": payment.amount,
            "country": payment.country,
            "failure_reason": reason,
            "recommended_action": "RETRY",
            "message": "Temporary failure detected. Retry the payment later."
        }

    # 3. Insufficient funds
    elif reason == "INSUFFICIENT_FUNDS":
        return {
            "amount": payment.amount,
            "country": payment.country,
            "failure_reason": reason,
            "recommended_action": "RETRY",
            "message": "Insufficient funds. Ask the customer to use another payment method or retry after adding funds."
        }

    # 4. Card declined
    elif reason == "CARD_DECLINED":
        return {
            "amount": payment.amount,
            "country": payment.country,
            "failure_reason": reason,
            "recommended_action": "USE_ALTERNATIVE_METHOD",
            "message": "Card was declined. Try another payment method."
        }

    # 5. Network timeout
    elif reason == "TIMEOUT":
        return {
            "amount": payment.amount,
            "country": payment.country,
            "failure_reason": reason,
            "recommended_action": "RETRY",
            "message": "Payment request timed out. Retry with a safe delay."
        }

    # 6. Currency-related failure
    elif reason == "CURRENCY_NOT_SUPPORTED":
        return {
            "amount": payment.amount,
            "country": payment.country,
            "failure_reason": reason,
            "recommended_action": "CHANGE_CURRENCY",
            "message": "The selected currency is not supported. Try a supported currency."
        }

    # 7. Unknown failure
    else:
        return {
            "amount": payment.amount,
            "country": payment.country,
            "failure_reason": reason,
            "recommended_action": "RETRY",
            "message": "Unknown failure. Retry with a safe strategy."
        }


# --------------------------------------------------
# PAYMENT RETRY DECISION
# --------------------------------------------------

@app.post("/payment/retry")
def retry_payment(payment: PaymentRequest):

    reason = payment.failure_reason.upper()

    # Technical error
    if reason == "TECHNICAL_ERROR":
        return {
            "status": "RETRY_SCHEDULED",
            "strategy": "EXPONENTIAL_BACKOFF",
            "retry_after_seconds": 30,
            "max_retries": 3,
            "message": "Temporary technical error. Retry after 30 seconds."
        }

    # Currency not supported
    elif reason == "CURRENCY_NOT_SUPPORTED":
        return {
            "status": "FALLBACK_REQUIRED",
            "strategy": "ALTERNATIVE_CURRENCY",
            "retry_after_seconds": 0,
            "max_retries": 0,
            "message": "Currency is not supported. Use a supported currency."
        }

    # 3DS required
    elif reason == "3DS_REQUIRED":

        if payment.three_ds_supported:
            return {
                "status": "ACTION_REQUIRED",
                "strategy": "3DS_AUTHENTICATION",
                "retry_after_seconds": 0,
                "max_retries": 1,
                "message": "Start 3DS authentication before retrying."
            }

        else:
            return {
                "status": "FALLBACK_REQUIRED",
                "strategy": "ALTERNATIVE_PAYMENT",
                "retry_after_seconds": 0,
                "max_retries": 0,
                "message": "3DS is not supported. Use another payment method."
            }

    # Insufficient funds
    elif reason == "INSUFFICIENT_FUNDS":
        return {
            "status": "RETRY_LATER",
            "strategy": "CUSTOMER_ACTION",
            "retry_after_seconds": 3600,
            "max_retries": 1,
            "message": "Customer needs to add funds or use another payment method."
        }

    # Card declined
    elif reason == "CARD_DECLINED":
        return {
            "status": "FALLBACK_REQUIRED",
            "strategy": "ALTERNATIVE_PAYMENT",
            "retry_after_seconds": 0,
            "max_retries": 0,
            "message": "Card was declined. Use an alternative payment method."
        }

    # Timeout
    elif reason == "TIMEOUT":
        return {
            "status": "RETRY_SCHEDULED",
            "strategy": "EXPONENTIAL_BACKOFF",
            "retry_after_seconds": 30,
            "max_retries": 3,
            "message": "Payment timed out. Retry after a safe delay."
        }

    # Unknown failure
    else:
        return {
            "status": "RETRY_SCHEDULED",
            "strategy": "SAFE_RETRY",
            "retry_after_seconds": 60,
            "max_retries": 1,
            "message": "Unknown failure. Retry using a safe strategy."
        }