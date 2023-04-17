from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from sqlalchemy.orm import scoped_session, sessionmaker, Query
from app import login_manager

# dialect+driver://username:password@host:port/database

engine = create_engine('postgresql://username:password@host:port/database', convert_unicode=True, echo=False,
                       pool_size=50, max_overflow=30)
Base = declarative_base()
Base.metadata.reflect(engine)


class User(Base, UserMixin):
    __table__ = Base.metadata.tables['AdminUser']

    def get_id(self):
        return self.admin_id


class Player(Base):
    __table__ = Base.metadata.tables['User']


class Referral(Base):
    __table__ = Base.metadata.tables['Referral']


class AdminDeploy(Base):
    __table__ = Base.metadata.tables['AdminDeploy']


class Deployment(Base):
    __table__ = Base.metadata.tables['Deployment']


class DeployLocation(Base):
    __table__ = Base.metadata.tables['DeployLocation']


class Script(Base):
    __table__ = Base.metadata.tables['Script']


class DataSource(Base):
    __table__ = Base.metadata.tables['DataSource']


class Data(Base):
    __table__ = Base.metadata.tables['Data']


class Response(Base):
    __table__ = Base.metadata.tables['Response']


class AdminProject(Base):
    __table__ = Base.metadata.tables['AdminProject']


db_session = scoped_session(sessionmaker(bind=engine))


@login_manager.user_loader
def user_loader(adminid):
    return db_session.query(User).filter_by(admin_id=adminid).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = db_session.query(User).filter_by(admin_name=username).first()
    return user if user else None


