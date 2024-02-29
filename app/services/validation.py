from fastapi import HTTPException, status

from app.models import CharityProject
from app.schemas import CharityProjectUpdate


def project_validation(project: CharityProject, obj_in: CharityProjectUpdate):
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
