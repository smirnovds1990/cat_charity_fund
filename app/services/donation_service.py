from datetime import datetime
from typing import Union

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import MIN_INT_FIELD_AMOUNT
from app.crud import charity_project_crud, donation_crud
from app.models import CharityProject, Donation, User
from app.schemas import (
    CharityProjectCreate, CharityProjectUpdate, DonationCreate
)
from app.services.utils import get_available_donation, get_open_project


class InvestingService:

    def __init__(self, session: AsyncSession):
        self.session = session

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
        project_name: str
    ):
        project_id = await charity_project_crud.get_project_id_by_name(
            project_name, self.session
        )
        if project_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Проект с таким именем уже существует!'
            )

    def __check_project_is_invested(self, project: CharityProject):
        if project.invested_amount > MIN_INT_FIELD_AMOUNT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='В проект были внесены средства, не подлежит удалению!'
            )

    async def __add_commit_and_refresh_new_donation_and_project(
        self,
        invested_object: Union[CharityProject, Donation]
    ):
        self.session.add(invested_object)
        await self.session.commit()
        await self.session.refresh(invested_object)
        return invested_object

    def __project_validation(
        self,
        project: CharityProject,
        obj_in: CharityProjectUpdate
    ):
        if project.fully_invested:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Закрытый проект нельзя редактировать!'
            )
        if (
            obj_in.full_amount is not None and
            obj_in.full_amount < project.invested_amount
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Нелья установить значение full_amount меньше уже вложенной суммы.'
            )

    async def create_new_donation(
        self,
        obj_in: DonationCreate,
        user: User
    ):
        new_object = await donation_crud.create(obj_in, self.session, user)
        open_project = await get_open_project(self.session)
        invested_donation = self.__distribute_money(
            obj_in=new_object,
            open_project=open_project,
            available_donation=None
        )
        return await self.__add_commit_and_refresh_new_donation_and_project(
            invested_object=invested_donation
        )

    async def create_new_project(
        self,
        obj_in: CharityProjectCreate
    ):
        await self.__check_name_duplicate(obj_in.name)
        new_object = await charity_project_crud.create(
            obj_in, self.session
        )
        available_donation = await get_available_donation(self.session)
        invested_project = self.__distribute_money(
            obj_in=new_object,
            open_project=None,
            available_donation=available_donation
        )
        return await self.__add_commit_and_refresh_new_donation_and_project(
            invested_object=invested_project
        )

    async def update_project(
        self,
        project: CharityProject,
        obj_in: CharityProjectUpdate
    ):
        self.__project_validation(project, obj_in)
        if obj_in.name is not None:
            await self.__check_name_duplicate(obj_in.name)
        project = await charity_project_crud.update(
            project, obj_in, self.session
        )
        return project

    async def delete_project(
            self,
            project: CharityProject
    ):
        self.__check_project_is_invested(project)
        project = await charity_project_crud.remove(project, self.session)
        return project
