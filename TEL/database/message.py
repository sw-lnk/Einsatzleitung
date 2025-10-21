from sqlmodel import select

from TEL.database import database
from TEL.model import Message

async def create_message(message: Message) -> Message | None:
    with database.get_session() as session:
        session.add(message)
        session.commit()
        session.refresh(message)
        return message

def __delete_message(message_id: int) -> None:
     with database.get_session() as session:
        msg = session.exec(select(Message).where(Message.id == message_id)).first()
        session.delete(msg)
        session.commit()

def get_all_messages() -> list[Message] | None:
    with database.get_session() as session:
        return session.exec(select(Message).order_by(Message.created_at.desc())).all()

def get_message_mission(mission_id: int) -> list[Message] | None:
    with database.get_session() as session:
        return session.exec(select(Message).where(Message.mission_id == mission_id).order_by(Message.created_at.desc())).all()