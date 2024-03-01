from sqlalchemy import Column, String, Text

from app.constants import MAX_STR_FIELD_LENGTH
from .core import CoreClass


class CharityProject(CoreClass):
    name = Column(String(MAX_STR_FIELD_LENGTH))
    description = Column(Text)
