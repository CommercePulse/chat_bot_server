from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
import datetime

    
class Status(str,Enum):
    RUNNING = "RUNNING"
    STOP = "STOP"
    TERMINATE = "TERMINATE"

Base = declarative_base()

class BotVectorNamespace(Base):
    __tablename__ = 'bot_vector_namespace'

    id = Column(Integer, primary_key=True, autoincrement=True)
    bot_name = Column(String(20), nullable=False)
    namespace_id = Column(String(20), nullable=False, unique=True)
    namespace_name = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self) -> str:
        return f"BotVectorNameSpace(id={self.id}, bot_name={self.bot_name}, namespace_name={self.namespace_name}, namespace_id={self.namespace_id}, created_at={self.created_at})"


class BotNamespaceChatLogs(Base):
    __tablename__ = "bot_namespace_chat_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    namespace_id = Column(String(20), nullable=False, unique=False)
    user_message = Column(String, nullable=False, unique=False)
    bot_response = Column(String, nullable=False, unique=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)

    def __repr__(self) -> str:
        return f"BotNamespaceChatLogs(id={self.id}, namespace_id={self.namespace_id}, user_message={self.user_message}, bot_response={self.bot_response}, created_at={self.created_at})"

class BotNamespaceFiles(Base):
    __tablename__ = "bot_namespace_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    namespace_id = Column(String(20), nullable=False, unique=False)
    name = Column(String, nullable=False, unique=False)
    size = Column(String, nullable=False, unique=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.now)
    # status: Literal["pending", "completed", "failed"] = Field(..., description="The status of the upload process")
    def __repr__(self) -> str:
        return f"BotNamespaceFiles(id={self.id}, namespace_id={self.namespace_id}, name={self.name}, size={self.size}, created_at={self.created_at})"

  
    