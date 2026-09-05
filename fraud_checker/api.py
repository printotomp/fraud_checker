"""Minimal HTTP API around the fraud scorer.

Run locally with:
    uvicorn fraud_checker.api:app --reload

POST an order to /check-order and get back a verdict + which rules fired.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from .models import Address, Order
from .scorer import FraudScorer

app = FastAPI(
    title="Small-Business Order Fraud Checker",
    description=(
        "A lightweight, explainable fraud-risk API for indie e-commerce "
        "sellers who can't afford enterprise fraud tooling."
    ),
    version="0.1.0",
)

scorer = FraudScorer()


class AddressIn(BaseModel):
    country: str
    postcode: str
    city: str = ""


class OrderIn(BaseModel):
    order_id: str
    customer_email: str
    customer_id: Optional[str] = None
    amount: float
    currency: str = "GBP"
    billing_address: AddressIn
    shipping_address: AddressIn
    ip_country: Optional[str] = None
    created_at: datetime
    is_new_customer: bool = True
    previous_order_count: int = 0
    recent_order_timestamps: List[datetime] = []
    items_count: int = 1
    payment_method: str = "card"
    card_country: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/check-order")
def check_order(order_in: OrderIn):
    order = Order(
        order_id=order_in.order_id,
        customer_email=order_in.customer_email,
        customer_id=order_in.customer_id,
        amount=order_in.amount,
        currency=order_in.currency,
        billing_address=Address(**order_in.billing_address.dict()),
        shipping_address=Address(**order_in.shipping_address.dict()),
        ip_country=order_in.ip_country,
        created_at=order_in.created_at,
        is_new_customer=order_in.is_new_customer,
        previous_order_count=order_in.previous_order_count,
        recent_order_timestamps=order_in.recent_order_timestamps,
        items_count=order_in.items_count,
        payment_method=order_in.payment_method,
        card_country=order_in.card_country,
    )
    report = scorer.score(order)
    return report.to_dict()
