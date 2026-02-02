from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class ChatLog(Base):
    __tablename__ = 'chat_logs'
    id = Column(Integer, primary_key=True)
    user_query = Column(String)
    bot_response = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Kết nối và tạo bảng tự động
engine = create_engine('sqlite:///data/database/history.db')
Base.metadata.create_all(engine)