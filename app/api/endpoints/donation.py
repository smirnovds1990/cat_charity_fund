from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import AllDonationsDB, DonationCreate, UserDonationDB
from app.services.donation_service import service


router = APIRouter()


@router.get(
    '/',
    response_model=list[AllDonationsDB],
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(session: AsyncSession = Depends(get_async_session)):
    """Только для суперюзера."""
    donations = await donation_crud.get_multi(session)
    if not donations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Ещё нет пожертвований.'
        )
    return donations


@router.post(
    '/',
    response_model=UserDonationDB,
    response_model_exclude_none=True
)
async def create_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Только для авторизованных пользователей."""
    return await service.create_new_donation(
        obj_in=donation, session=session, user=user
    )


@router.get(
    '/my',
    response_model=list[UserDonationDB]
)
async def get_user_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Только для авторизованных пользователей."""
    return await donation_crud.get_multi(session, user)
