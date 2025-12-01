'''
Generate Demo Data
'''
from sqlmodel import select

from TEL.database.database import get_session, create_db_and_tables

from TEL import model
from TEL.authentication import get_password_hash

def create_demo_user() -> model.UserInfo:
    print('Create Demo User...')
    password = get_password_hash('Password.1234')
    admin = model.User(
        username='admin',
        hashed_password=password,
        name='Demo Admin Permission',
        email='admin@example.com',
        permission=model.Permission.admin,
    )
    write = model.User(
        username='write',
        hashed_password=password,
        name='Demo Write Permission',
        email='write@example.com',
        permission=model.Permission.write,
    )
    read = model.User(
        username='read',
        hashed_password=password,
        name='Demo Read Permission',
        email='read@example.com',
        permission=model.Permission.read,
    )    
    user = model.User(
        username='user',
        hashed_password=password,
        name='Demo No Permission',
        email='user@example.com',
    )
    
    with get_session() as session:
        session.add(admin)
        session.add(write)
        session.add(read)
        session.add(user)
        session.commit()
        session.refresh(admin)
    
    return model.UserInfo.model_validate(admin)

messages = [
    'Erste Rückmeldung von der Est: Loremipsum Loremipsum Loremipsum Loremipsum Loremipsum Loremipsum Loremipsum Loremipsum Loremipsum Loremipsum Loremipsum',
    'Folgemeldung: Lage unter Kontrolle, Einsatzdauer unbekannt.',
    'Folgemeldung: Maßnahmen werden zurückgenommen, Einsatzstelle an Eigentümer übergeben.',
    'Abschlussmeldung: Rücken ein.',
]

missions = [
    {'id': 1,
     'mission': model.Mission(
        id=1,
        label='123456789',
        street='Muster Straße',
        street_no='1',
        zip_code='12345',
        status=model.Status.new,
        category=model.Category.th,
        comment='VU P klemmt'
    ),
    'messages': []
    },
    {'id': 2,
     'mission': model.Mission(
        id=2,
        label='223456789',
        street='Weg des Musters',
        street_no='7a',
        zip_code='12345',
        status=model.Status.in_progress,
        category=model.Category.fire,
        comment='Unklare Rauchentwicklung'
    ),
    'messages': [
        'Fl.MUS.1.HLF20.1 dem Einsatz zugeordnet.',
        'Fl.MUS.1.LF20.1 dem Einsatz zugeordnet.',
        'Fl.MUS.1.DLK23.1 dem Einsatz zugeordnet.',
        ]
    },
    {'id': 3,
     'mission': model.Mission(
        id=3,
        label='323456789',
        street='Großestraße',
        street_no='112',
        zip_code='12345',
        status=model.Status.closed,
        category=model.Category.th,
        comment='Baum auf Straße'
    ),
    'messages': [
        'Fl.MUS.2.HLF20.1 dem Einsatz zugeordnet.',
        'Fl.MUS.2.RW2.1 dem Einsatz zugeordnet.',
        'Fl.MUS.2.ELW1.1 dem Einsatz zugeordnet.',] + messages
    },
    {'id': 4,
     'mission': model.Mission(
        id=4,
        label='423456789',
        street='Muster Weg / Muster Straße',
        zip_code='12345',
        status=model.Status.archived,
        category=model.Category.cbrn,
        comment='Ölspur'
    ),
    'messages': []
    },
]

def create_demo_mission(user: model.UserInfo) -> None:    
    print('Create Demo Missions...')
    with get_session() as session:
        for m in missions:
            mission = m['mission']
            first_msg = model.Message(
                content='Einsatz erstellt.',
                prio=model.Priority.low,
                mission_id=m['id'],
                user_id=user.id
            )
            session.add_all([mission, first_msg])
            for msg in m['messages']:
                session.add(
                    model.Message(
                        content=msg,
                        prio=model.Priority.low,
                        mission_id=m['id'],
                        user_id=user.id
            ))
            session.commit()

def create_demo_messages(user: model.UserInfo):
    print('Create Demo Messages...')
    with get_session() as session:
        for mis in session.exec(select(model.Mission)).all():
            for msg in messages:
                session.add(
                    model.Message(
                        content=msg,
                        user_id=user.id,
                        mission_id=mis.id,
                    ),
                )
        session.commit()

def create_demo_units():
    print('Create Demo Units...')
    with get_session() as session:
        session.add_all([
            model.Unit(label='Fl.MUS.1.HLF20.1', status=0, status_prev=4, zf=1, gf=1, ms=6, agt=4, mission_id=2),
            model.Unit(label='Fl.MUS.1.LF20.1', status=5, status_prev=3, gf=1, ms=6, agt=5, mission_id=2),
            model.Unit(label='Fl.MUS.1.DLK23.1', status=4, vf=1, ms=2, agt=1, mission_id=2),
            model.Unit(label='Fl.MUS.1.ELW1.1', status=1, vf=1, zf=1, ms=1, agt=1),
            model.Unit(label='Fl.MUS.1.MTF.1', status=6),
            
            model.Unit(label='Fl.MUS.2.HLF20.1', status=3, gf=1, ms=8, agt=5, mission_id=3),
            model.Unit(label='Fl.MUS.2.LF20.1', status=2),
            model.Unit(label='Fl.MUS.2.RW2.1', status=3, zf=1, gf=1, ms=1, agt=1, mission_id=3),
            model.Unit(label='Fl.MUS.2.ELW1.1', status=1, zf=1, gf=2, mission_id=3),
            model.Unit(label='Fl.MUS.2.MTF.1', status=2),
        ])
        session.commit()

if __name__ in {"__main__", "__mp_main__"}:
    print('### Demo Data Creation ###')
    
    create_db_and_tables()
    admin = create_demo_user()
    create_demo_mission(admin)
    # create_demo_messages(admin)
    create_demo_units()
    
    print('### Ready for Testing ###')
