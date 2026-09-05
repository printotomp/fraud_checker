"""Data models for orders evaluated by the fraud checker."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Address:
    country: str
    postcode: str
    city: str = ""


@dataclass
class Order:
    """A single incoming order to be scored for fraud risk.

    Only the fields a small store can realistically capture at checkout
    are required — this is meant to work with whatever a lightweight
    e-commerce stack (Shopify, WooCommerce, a custom cart, etc.) already
    has, not a full identity-verification pipeline.
    """

    order_id: str
    customer_email: str
    customer_id: Optional[str]
    amount: float
    currency: str
    billing_address: Address
    shipping_address: Address
    ip_country: Optional[str]
    created_at: datetime
    is_new_customer: bool = True
    previous_order_count: int = 0
    # Timestamps of the customer's other orders in the recent window,
    # used for velocity checks. Caller is responsible for supplying a
    # reasonable window (e.g. last 24h) — the checker does not query
    # any datastore itself.
    recent_order_timestamps: list[datetime] = field(default_factory=list)
    items_count: int = 1
    payment_method: str = "card"
    card_country: Optional[str] = None
