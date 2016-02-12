from dbschema import *
from dbsession import session

print len(session.query(Agents).all())
