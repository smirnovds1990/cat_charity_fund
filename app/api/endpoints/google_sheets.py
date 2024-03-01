from typing import Union

from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud import charity_project_crud
from app.services.google_sheets import google_service


router = APIRouter()


@router.post(
    '/',
    response_model=list[dict[str, Union[str, int]]],
    dependencies=[Depends(current_superuser)],
)
async def get_report(
    session: AsyncSession = Depends(get_async_session),
    wrapper_services: Aiogoogle = Depends(get_service)

):
    """Только для суперюзеров."""
    closed_projects = (
        await charity_project_crud.get_projects_by_completion_rate(session)
    )
    if not closed_projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Нет закрытых проектов.'
        )
    spreadsheetid = await google_service.spreadsheets_create(wrapper_services)
    await google_service.set_user_permissions(spreadsheetid, wrapper_services)
    await google_service.spreadsheets_update_value(
        spreadsheetid,
        closed_projects,
        wrapper_services
    )
    return closed_projects
