from datetime import datetime

from sqlalchemy import types, Column
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Run(Base):
    __tablename__ = 'runs'

    id = Column(types.DATE, primary_key=True)
    blob = Column(types.JSON())


class Experiment(Base):
    __tablename__ = 'experiments'

    id = Column(types.INTEGER,
                primary_key=True,
                autoincrement=True)
    executed_at = Column(types.DATE)
    command = Column(types.String)
    git_repo = Column(types.String)
    git_commit_hash = Column(types.String(12))
    metrics = Column(types.JSON)
    username = Column(types.String)
    github_name = Column(types.String)
    github_email = Column(types.String)
    created_at = Column(types.DATE, default=datetime.now)
