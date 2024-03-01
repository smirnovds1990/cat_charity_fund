from datetime import datetime, timedelta

from aiogoogle import Aiogoogle

from app.constants import DATE_FORMAT
from app.core.config import settings


class GoogleService:

    async def spreadsheets_create(self, wrapper_services: Aiogoogle) -> str:
        now_date_time = datetime.now().strftime(DATE_FORMAT)
        service = await wrapper_services.discover('sheets', 'v4')
        spreadsheet_body = {
            'properties': {'title': f'Отчёт на {now_date_time}',
                           'locale': 'ru_RU'},
            'sheets': [{'properties': {'sheetType': 'GRID',
                                       'sheetId': 0,
                                       'title': 'Лист1',
                                       'gridProperties': {'rowCount': 100,
                                                          'columnCount': 11}}}]
        }
        response = await wrapper_services.as_service_account(
            service.spreadsheets.create(json=spreadsheet_body)
        )
        spreadsheetid = response['spreadsheetId']
        return spreadsheetid

    async def set_user_permissions(
        self,
        spreadsheetid: str,
        wrapper_services: Aiogoogle
    ) -> None:
        permissions_body = {'type': 'user',
                            'role': 'writer',
                            'emailAddress': settings.email}
        service = await wrapper_services.discover('drive', 'v3')
        await wrapper_services.as_service_account(
            service.permissions.create(
                fileId=spreadsheetid,
                json=permissions_body,
                fields="id"
            ))

    async def spreadsheets_update_value(
            self,
            spreadsheetid: str,
            closed_projects: list,
            wrapper_services: Aiogoogle
    ) -> None:
        now_date_time = datetime.now().strftime(DATE_FORMAT)
        service = await wrapper_services.discover('sheets', 'v4')
        table_values = [
            ['Отчёт от', now_date_time],
            ['Топ проектов по скорости закрытия'],
            ['Название проекта', 'Время сбора', 'Описание']
        ]
        for project in closed_projects:
            new_row = [
                project.name,
                str(timedelta(seconds=project.duration)),
                project.description
            ]
            table_values.append(new_row)

        update_body = {
            'majorDimension': 'ROWS',
            'values': table_values
        }
        await wrapper_services.as_service_account(
            service.spreadsheets.values.update(
                spreadsheetId=spreadsheetid,
                range='A1:E30',
                valueInputOption='USER_ENTERED',
                json=update_body
            )
        )


google_service = GoogleService()
