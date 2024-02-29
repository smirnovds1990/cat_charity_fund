from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectCreateDB, CharityProjectDB,
    CharityProjectUpdate, GetCharityProjectDB
)
from app.services.donation_service import service
from app.api.utils import get_existing_project_or_404


router = APIRouter()


@router.get('/', response_model=list[GetCharityProjectDB])
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session)
):
    projects = await charity_project_crud.get_multi(session)
    if not projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Ещё нет проектов.'
        )
    return projects


@router.post(
    '/',
    response_model=CharityProjectCreateDB,
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True
)
async def create_charity_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    return await service.create_new_project(
        obj_in=charity_project, session=session
    )


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    project = await get_existing_project_or_404(project_id, session)
    return await service.update_project(
        project=project, obj_in=obj_in, session=session
    )


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Только для суперюзеров."""
    project = await get_existing_project_or_404(project_id, session)
    return await service.delete_project(project, session)
