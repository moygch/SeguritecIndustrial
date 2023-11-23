from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

# engine = create_engine('mysql://root:@localhost/seguritec')
engine = create_engine('mysql://moygch:Re@lmois10@moygch.mysql.pythonanywhere-services.com/moygch$seguritec')
# engine = create_engine('sqlite:///BD_seguritec')
db_session = scoped_session(sessionmaker(bind=engine))

Database = declarative_base()