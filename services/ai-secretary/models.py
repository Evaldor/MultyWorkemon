from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class RequestHistory(Base):
    __tablename__ = 'request_history'

    id = Column(Integer, primary_key=True, index=True)
    channel = Column(String, nullable=False)
    username = Column(String, nullable=False)
    request_text = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    action = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)