from sqlalchemy import  select, MetaData,delete
from models.schemas import BotVectorNamespace, BotNamespaceChatLogs,BotNamespaceFiles
from sqlalchemy.orm import Session
from config.sqlite import engine
import datetime
from typing import List

class BotNamespaceQueries:

    async def execute_create_command(self,save_info: BotVectorNamespace | BotNamespaceFiles):
         
        with Session(engine) as session:
            session.add(save_info)
            session.commit()

    async def get_bot_info(self,namespace_id: str):
        with Session(engine) as session:
            data = select(BotVectorNamespace).where(BotVectorNamespace.namespace_id == namespace_id)
            data = session.scalars(data).all()
            return data

    async def log_chat_interaction(self,namespace_id: str, user: str, bot: str):
        with Session(engine) as session:
            chat_interaction = BotNamespaceChatLogs(namespace_id=namespace_id,
                                                    user_message=user,
                                                    bot_response=bot)
            session.add(chat_interaction)
            session.commit()

    async def get_chat_interaction(self,namespace_id: str):
        with Session(engine) as session:
            data = select(BotNamespaceChatLogs).where(BotNamespaceChatLogs.namespace_id == namespace_id).order_by(BotNamespaceChatLogs.created_at.asc())
            data = session.scalars(data).all()
            return data

    async def get_file_info(self,namespace_id: str):
        with Session(engine) as session:
            data = select(BotNamespaceFiles).where(BotNamespaceFiles.namespace_id == namespace_id)
            data = session.scalars(data).all()
            return data
        
    async def get_all_tables(self):
        # Create a MetaData object to reflect the database schema
        metadata = MetaData()
        # Reflect the schema from the engine (database)
        metadata.reflect(bind=engine)
        # Get the table names
        tables = metadata.tables.keys()
        print(list(tables))
        return list(tables)

    async def delete_files(self, ids: List[int]):
        with Session(engine) as session:
            # Delete entries where namespace_id is in the given list
            stmt = delete(BotNamespaceFiles).where(BotNamespaceFiles.id.in_(ids))
            session.execute(stmt)
            session.commit()
        
    