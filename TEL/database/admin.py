from sqlmodel import Session, select

from TEL.database import database
from TEL.model import User, UserInfo

def get_all_user() -> list[UserInfo]:
    with Session(database.engine) as session:
        all_user = session.exec(select(User)).all()
        return [UserInfo.model_validate(user) for user in all_user]
