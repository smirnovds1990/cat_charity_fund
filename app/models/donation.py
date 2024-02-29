from sqlalchemy import Column, ForeignKey, Integer, Text

from .core import CoreClass


class Donation(CoreClass):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text, nullable=True)
