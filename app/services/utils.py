from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def get_open_project(session: AsyncSession):
    open_project = await session.execute(
        select(CharityProject).where(CharityProject.fully_invested.is_(False))
    )
    open_project = open_project.scalars().first()
    return open_project


async def get_available_donation(
    session: AsyncSession
):
    available_donation = await session.execute(
        select(Donation).where(Donation.fully_invested.is_(False))
    )
    available_donation = available_donation.scalars().first()
    return available_donation
