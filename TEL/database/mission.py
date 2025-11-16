from sqlmodel import select

from TEL.database import database
from TEL.model import Mission, Status, Unit

async def create_mission(mission: Mission) -> Mission | None:
    with database.get_session() as session:
        session.add(mission)
        session.commit()
        session.refresh(mission)
        return mission

def get_all_mission(archived: bool = True) -> list[Mission] | None:
    with database.get_session() as session:
        if archived:
            return session.exec(select(Mission).where(Mission.status != Status.archived)).all()
        else:
            return session.exec(select(Mission)).all()

def get_mission_by_label(label: str) -> Mission | None:
    with database.get_session() as session:
        return session.exec(select(Mission).where(Mission.label == label)).first()

def get_mission_by_id(mission_id: int) -> Mission | None:
    with database.get_session() as session:
        return session.exec(select(Mission).where(Mission.id == mission_id)).first()

def get_mission_units(mission_id: int) -> list[Unit] | None:
    with database.get_session() as session:
        mission = session.exec(select(Mission).where(Mission.id == mission_id)).first()
        return mission.units
    
async def update_mission_data(mission: Mission) -> Mission:
    return await create_mission(mission)

async def archiv_mission(mission_id: int):
    mission = get_mission_by_id(mission_id)
    mission.status = Status.archived
    return await update_mission_data(mission)

async def reactivate_mission(mission_id: int):
    mission = get_mission_by_id(mission_id)
    mission.status = Status.closed
    return await update_mission_data(mission)