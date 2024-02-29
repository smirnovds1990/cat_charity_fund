from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import charity_project_crud


async def get_existing_project_or_404(
        project_id: int,
        session: AsyncSession,
):
    project = await charity_project_crud.get(project_id, session)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Проект не найден!'
        )
    return project
