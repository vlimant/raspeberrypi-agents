from dbschema import *
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:////home/vlimant/database/Record.db')
Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def get_session():
    engine = create_engine('sqlite:////home/vlimant/database/Record.db')
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    MYDBSession = sessionmaker(bind=engine)
    mysession = MYDBSession()
    return mysession
