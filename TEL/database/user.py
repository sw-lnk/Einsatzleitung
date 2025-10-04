from sqlmodel import Session, select

from TEL.database import database
from TEL.model.user import User, UserInfo

async def create_user(user: User) -> UserInfo | None:
    with Session(database.engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return UserInfo.model_validate(user)

def _get_user_by_username(username: str) -> User | None:
    with Session(database.engine) as session:
        return session.exec(select(User).where(User.username == username)).first()

def _get_user_by_id(user_id: int) -> User:    
    with Session(database.engine) as session:
        return session.exec(select(User).where(User.id == user_id)).first()

def get_user_by_username(username: str) -> UserInfo | None:
    return UserInfo.model_validate(_get_user_by_username(username))

def get_user_by_id(user_id: int) -> UserInfo:    
    return UserInfo.model_validate(_get_user_by_id(user_id))

async def update_user_data(user: User) -> User:
    with Session(database.engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
