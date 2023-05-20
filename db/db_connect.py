import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
#from config import *

logger = logging.getLogger('logger')

"""Эта часть кода для PostgreSQL"""
# DATABASE = {
#     'drivername': 'mysql+mysqlconnector',
#     'host': f'{HOST}',
#     'port': '3306',
#     'username': f'{DB_USERNAME}',
#     'password': f'{DB_PASSWORD}',
#     'database': f'{DATABASE}'
# }
#url_engine = create_engine(f"{DATABASE['drivername']}://{DATABASE['username']}:{DATABASE['password']}@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['database']}")

url_engine = create_engine('sqlite:///sqlite3.db')

Base = declarative_base()

Session = sessionmaker(bind=url_engine)
session = Session()
