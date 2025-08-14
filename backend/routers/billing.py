"""
Billing router
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

class SubscriptionResponse(BaseModel):
    id: str
    plan: str
    status: str
    current_period_start: datetime
    current_period_end: datetime

class InvoiceResponse(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    created_at: datetime

@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(token: str = Depends(security)):
    """Get current user subscription"""
    # TODO: Implement subscription retrieval from Stripe
    return SubscriptionResponse(
        id="dummy_sub_id",
        plan="basic",
        status="active",
        current_period_start=datetime.now(),
        current_period_end=datetime.now()
    )

@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(token: str = Depends(security)):
    """Get user invoices"""
    # TODO: Implement invoice retrieval from Stripe
    return []

@router.post("/create-checkout-session")
async def create_checkout_session(token: str = Depends(security)):
    """Create Stripe checkout session"""
    # TODO: Implement Stripe checkout session creation
    return {"checkout_url": "https://checkout.stripe.com/dummy"}

@router.post("/create-portal-session")
async def create_portal_session(token: str = Depends(security)):
    """Create Stripe customer portal session"""
    # TODO: Implement Stripe customer portal session creation
    return {"portal_url": "https://billing.stripe.com/dummy"}