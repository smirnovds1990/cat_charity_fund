# Кошачий благотворительный фонд (cat_charity_fund)
Приложение для благотворительного фонда поддержки котов. 
Фонд собирает пожертвования на различные целевые проекты: на медицинское обслуживание нуждающихся хвостатых, на обустройство кошачьей колонии в подвале, на корм оставшимся без попечения кошкам — на любые цели, связанные с поддержкой кошачьей популяции.
Пользователи регистрируются и могут отправлять пожертвования в фонд. Пожертвования распределяются автоматически по проектам фонда в соответствии датой создания проекта от ранних к поздним.

## Технологии

- [Python](https://docs.python.org/3/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/latest/)
- [Starlette](https://www.starlette.io/)
- [SQLAlchemy](https://docs.sqlalchemy.org/en/20/)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/)
- [Uvicorn](https://www.uvicorn.org/)

## Установка
Скачать репозиторий, установить виртуальное окружение и зависимости.

```sh
git clone https://github.com/smirnovds1990/cat_charity_fund
python -m venv venv (для Unix python3)
source venv/Scripts/activate (для Unix venv/bin/activate)
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Запуск проекта

```sh
cd cat_charity_fund
uvicorn app.main:app --reload
```
Перейти по адресу http://127.0.0.1:8000/docs для просмотра OpenAPI-документации.

###### Автор: [https://github.com/smirnovds1990](https://github.com/smirnovds1990)
