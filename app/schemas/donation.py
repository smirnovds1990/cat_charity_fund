from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.constants import MIN_INT_FIELD_AMOUNT


class DonationCreate(BaseModel):
    full_amount: int = Field(gt=MIN_INT_FIELD_AMOUNT)
    comment: Optional[str]


class UserDonationDB(DonationCreate):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class AllDonationsDB(UserDonationDB):
    user_id: int
    invested_amount: int
    fully_invested: bool
