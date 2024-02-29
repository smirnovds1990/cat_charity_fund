from datetime import datetime
from typing import Union

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import MIN_AMOUNT
from app.crud import charity_project_crud, donation_crud
from app.models import CharityProject, Donation, User
from app.schemas import (
    CharityProjectCreate, CharityProjectUpdate, DonationCreate
)
from app.services.utils import get_available_donation, get_open_project
from app.services.validation import project_validation


class InvestingService:

    def __set_money_to_donations_and_projects(
            self,
            donation: Donation,
            project: CharityProject,
    ):
        project_rest = project.full_amount - project.invested_amount
        donation_rest = donation.full_amount - donation.invested_amount
        rest = project_rest - donation_rest
        if rest >= 0:
            project.invested_amount = (
                project.invested_amount + donation_rest
            )
            donation.invested_amount = donation.full_amount
            donation.fully_invested = True
            donation.close_date = datetime.now()
        else:
            project.invested_amount = project.full_amount
            project.fully_invested = True
            project.close_date = datetime.now()
            donation.invested_amount = (
                donation.invested_amount + project_rest
            )
        if project.invested_amount == project.full_amount:
            project.fully_invested = True
            project.close_date = datetime.now()
        return project, donation, rest

    def __distribute_money(
        self,
        obj_in: Union[Donation, CharityProject],
        open_project: Union[CharityProject, None],
        available_donation: Union[Donation, None]
    ):
        rest = 0
        if isinstance(obj_in, Donation):
            if open_project:
                self.__set_money_to_donations_and_projects(
                    obj_in, open_project
                )
            if rest < 0:
                self.__distribute_money(obj_in, open_project, None)
        elif isinstance(obj_in, CharityProject):
            if available_donation:
                self.__set_money_to_donations_and_projects(
                    available_donation, obj_in
                )
            if rest < 0:
                self.__distribute_money(obj_in, None, available_donation)
        return obj_in

    async def __check_name_duplicate(
        self,
        project_name: str,
        session: AsyncSession,
    ):
        project_id = await charity_project_crud.get_project_id_by_name(
            project_name, session
        )
        if project_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Проект с таким именем уже существует!'
            )

    def __check_project_is_invested(self, project: CharityProject):
        if project.invested_amount > MIN_AMOUNT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='В проект были внесены средства, не подлежит удалению!'
            )

    async def __add_commit_and_refresh_new_donation_and_project(
        self,
        session: AsyncSession,
        invested_object: Union[CharityProject, Donation]
    ):
        session.add(invested_object)
        await session.commit()
        await session.refresh(invested_object)
        return invested_object

    async def create_new_donation(
        self,
        obj_in: DonationCreate,
        user: User,
        session: AsyncSession
    ):
        new_object = await donation_crud.create(obj_in, session, user)
        open_project = await get_open_project(session)
        invested_donation = self.__distribute_money(
            obj_in=new_object,
            open_project=open_project,
            available_donation=None
        )
        return await self.__add_commit_and_refresh_new_donation_and_project(
            session=session, invested_object=invested_donation
        )

    async def create_new_project(
        self,
        obj_in: CharityProjectCreate,
        session: AsyncSession
    ):
        await self.__check_name_duplicate(obj_in.name, session)
        new_object = await charity_project_crud.create(obj_in, session)
        available_donation = await get_available_donation(session)
        invested_project = self.__distribute_money(
            obj_in=new_object,
            open_project=None,
            available_donation=available_donation
        )
        return await self.__add_commit_and_refresh_new_donation_and_project(
            session=session, invested_object=invested_project
        )

    async def update_project(
        self,
        project: CharityProject,
        obj_in: CharityProjectUpdate,
        session: AsyncSession
    ):
        project_validation(project, obj_in)
        if obj_in.name is not None:
            await self.__check_name_duplicate(obj_in.name, session)
        project = await charity_project_crud.update(project, obj_in, session)
        return project

    async def delete_project(
            self,
            project: CharityProject,
            session: AsyncSession
    ):
        self.__check_project_is_invested(project)
        project = await charity_project_crud.remove(project, session)
        return project


service = InvestingService()
