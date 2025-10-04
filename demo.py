'''
Generate Demo Data
'''
from sqlmodel import Session

from TEL.database.database import engine, create_db_and_tables
from TEL.model.user import User, Permission
from TEL.authentication import get_password_hash

def create_demo_user() -> None:
    password = get_password_hash('Password.1234')
    admin = User(
        username='admin',
        hashed_password=password,
        name='Demo Admin Permission',
        email='admin@example.com',
        permission=Permission.admin,
    )
    write = User(
        username='write',
        hashed_password=password,
        name='Demo Write Permission',
        email='write@example.com',
        permission=Permission.write,
    )
    read = User(
        username='read',
        hashed_password=password,
        name='Demo Read Permission',
        email='read@example.com',
        permission=Permission.read,
    )    
    user = User(
        username='user',
        hashed_password=password,
        name='Demo No Permission',
        email='user@example.com',
    )
    
    with Session(engine) as session:
        session.add(admin)
        session.add(write)
        session.add(read)
        session.add(user)
        session.commit()
        

if __name__ in {"__main__", "__mp_main__"}:
    create_db_and_tables()
    create_demo_user()