from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt

from app.constants import (
    MAX_STR_FIELD_LENGTH, MIN_INT_FIELD_AMOUNT, MIN_STR_FIELD_LENGTH
)


class CharityProjectCreate(BaseModel):
    name: str = Field(
        min_length=MIN_STR_FIELD_LENGTH, max_length=MAX_STR_FIELD_LENGTH
    )
    description: str = Field(min_length=MIN_STR_FIELD_LENGTH)
    full_amount: PositiveInt


class CharityProjectUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=MIN_STR_FIELD_LENGTH, max_length=MAX_STR_FIELD_LENGTH
    )
    description: Optional[str] = Field(None, min_length=MIN_STR_FIELD_LENGTH)
    full_amount: Optional[PositiveInt] = Field(None)

    class Config:
        extra = Extra.forbid


class GetCharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int = Field(MIN_INT_FIELD_AMOUNT)
    fully_invested: bool
    create_date: datetime

    class Config:
        orm_mode = True


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int = Field(MIN_INT_FIELD_AMOUNT)
    fully_invested: bool
    create_date: datetime
    close_date: datetime = Field(None)

    class Config:
        orm_mode = True


class CharityProjectCreateDB(CharityProjectCreate):
    id: int
    invested_amount: int = Field(MIN_INT_FIELD_AMOUNT)
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
