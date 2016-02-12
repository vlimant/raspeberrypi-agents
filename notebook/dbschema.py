import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, PickleType, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Agents(Base):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    ip = Column(String(30))
    workforce = Column(Integer)

    
class Workload(Base):
    __tablename__ = 'workload'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    status = Column(String(20)) ## available, running, done
    CPUh = Column(Integer) ## how much is needed
    remaining = Column(Integer) ## how much is remaing to be done
    memory = Column(Integer)
    ## ... 
    
#engine = create_engine('sqlite:////home/vlimant/database/Record.db')
#Base.metadata.create_all(engine)
