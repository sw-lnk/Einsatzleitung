from getpass import getpass
from sqlmodel import select

from TEL.model.user import User, Permission
from TEL.database.database import get_session, create_db_and_tables
from TEL.authentication import get_password_hash


create_db_and_tables()

print('Setup TEL')
print('Create Superuser...')

while True:
    username = input('Username: ')
    with get_session() as session:
        user_db = session.exec(select(User).where(User.username == username)).first()
        
        if not user_db:
            break
        
        print(f'Username: {username} already exists')
        
full_name = input('Name of the User: ')

while True:
    pwd1 = getpass('User Password: ')
    pwd2 = getpass('Confirm Password: ')
    if pwd1 == pwd2:
        break
    
    print('Password is not matching.')
    
email = input('E-Mail: ')
    
user = User(
    username=username,
    name=full_name,
    hashed_password=get_password_hash(pwd1),
    email=email,
    permission=Permission.admin
)
with get_session() as session:
    session.add(user)
    session.commit()
    session.refresh(user)

print('Creating User successful.')
