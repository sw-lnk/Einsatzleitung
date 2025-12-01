from sqlmodel import select
import uuid
import datetime as dt

from TEL.database import database
from TEL.model import Unit, User, Permission

async def create_unit(unit: Unit) -> Unit | None:
    new_user = User(
        username=unit.label,
        name=unit.label,
        email='',
        permission=Permission.unit,
        hashed_password=uuid.uuid1()
    )
    with database.get_session() as session:
        session.add_all(unit, new_user)
        session.commit()
        session.refresh(unit)
        return unit

async def __delete_unit(label: int) -> None:
     with database.get_session() as session:
        msg = session.exec(select(Unit).where(Unit.label == label)).first()
        session.delete(msg)
        session.commit()

async def update_unit_status(unit_label: str, status: int) -> Unit | None:
    with database.get_session() as session:
        unit = session.exec(select(Unit).where(Unit.label == unit_label)).first()
        if not unit:
            return None
        if unit.status not in [0, 5]:
            unit.status_prev = unit.status
        unit.update = dt.datetime.now()
        unit.status = status
        session.add(unit)
        session.commit()
        session.refresh(unit)
        return unit

async def update_unit(unit: Unit) -> Unit | None:
    with database.get_session() as session:
        unit.update = dt.datetime.now()
        session.add(unit)
        session.commit()
        session.refresh(unit)
        return unit
    
async def quit_unit_status(unit_label: str) -> Unit | None:
    with database.get_session() as session:
        unit = session.exec(select(Unit).where(Unit.label == unit_label)).first()
        if not unit:
            return None
        unit.update = dt.datetime.now()
        print(unit)
        if unit.status_prev:
            unit.status = unit.status_prev
        else:
            return unit
        session.add(unit)
        session.commit()
        session.refresh(unit)
        return unit

def get_unit(unit_label: str) -> Unit | None:
    with database.get_session() as session:
        return session.exec(select(Unit).where(Unit.label == unit_label)).first()

def get_all_units(status: int = None) -> list[Unit] | None:
    with database.get_session() as session:
        if not status:
            return session.exec(select(Unit).order_by(Unit.update)).all()
        else:
            return session.exec(select(Unit).where(Unit.status == status).order_by(Unit.update)).all()

def get_total_stuff() -> dict:
    all_units = get_all_units()
    vf = sum([unit.vf for unit in all_units])
    zf = sum([unit.zf for unit in all_units])
    gf = sum([unit.gf for unit in all_units])
    ms = sum([unit.ms for unit in all_units])
    agt = sum([unit.agt for unit in all_units])
    total = sum([vf, zf, gf, ms])
    return {
        'vf': vf if vf else 0,
        'zf': zf if zf else 0,
        'gf': gf if gf else 0,
        'ms': ms if ms else 0,
        'agt': agt if agt else 0,
        'total': total if total else 0,
    }
    