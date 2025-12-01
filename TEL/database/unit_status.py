from sqlmodel import select

from TEL.database import database
from TEL.model import UnitStatus

async def create_unit_status(
    status_number: int,
    unit_label: str,
    mission_id: int
    ) -> UnitStatus:
    status = UnitStatus(
        status_number=status_number,
        unit_label=unit_label,
        mission_id=mission_id,
    )
    with database.get_session() as session:
        session.add(status)
        session.commit()
        session.refresh(status)
        return status

def get_all_unit_status() -> list[UnitStatus] | None:
    with database.get_session() as session:
        return session.exec(select(UnitStatus).order_by(UnitStatus.timestamp.desc())).all()

def get_unit_status_mission(mission_id: int) -> list[UnitStatus] | None:
    with database.get_session() as session:
        return session.exec(select(UnitStatus).where(UnitStatus.mission_id == mission_id).order_by(UnitStatus.timestamp.desc())).all()
    