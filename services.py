from datetime import date
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from db.db_connect import Base, url_engine


class RawService(Base):
    __tablename__ = 'raw_service'

    id = Column(Integer, primary_key=True)
    service_name = Column(String)
    fix_percent = Column(Integer)
    id_employee = Column(Integer)

    def __init__(self, service_name: str, fix_percent: int, id_employee: int):
        self.service_name = service_name
        self.fix_percent = fix_percent
        self.id_employee = id_employee


class AddService(Base):
    __tablename__ = 'add_service'

    id = Column(Integer, primary_key=True)
    price = Column(Integer)
    sum_for_employee = Column(Integer)
    discount = Column(Integer)
    id_employee = Column(Integer)
    date_add = Column(Date, default=date.today())
    service = Column(Integer, ForeignKey('raw_service.id'))


Base.metadata.create_all(url_engine)




