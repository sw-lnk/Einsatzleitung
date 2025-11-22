import os
from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# =============================================================================
# USER MODEL
# =============================================================================

class Permission(str, Enum):
    read = 'read'
    write = 'write'
    unit = 'unit'
    admin = 'admin'
    
    
class UserInfo(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    name: str
    email: str
    permission: Permission | None = None
    
    def __str__(self):
        return self.name
    

class User(UserInfo, table=True):    
    hashed_password: str    
    created_at: datetime = Field(default_factory=datetime.now)
    messages: List["Message"] = Relationship(back_populates="user")


# =============================================================================
# MISSION MODEL
# =============================================================================

class Status(str, Enum):
    new = 'Neu'
    in_progress = 'In Arbeit'
    closed = 'Abgeschlossen'
    archived = 'Archiviert'


class Category(str, Enum):
    th = 'TH'
    fire = 'Brand'
    cbrn = 'CBRN'
    
    
class Mission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    label: str = Field(unique=True)
    street: str
    street_no: Optional[str] = None
    zip_code: Optional[str] = os.getenv('ZIP_CODE')
    category: Category
    status: Status = Status.new
    comment: Optional[str] = None
        
    changed_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    
    messages: List["Message"] = Relationship(back_populates="mission")
    units: List["Unit"] = Relationship(back_populates="mission")
    
    def address(self) -> str:
        return f"{' '.join([self.street, self.street_no])}, {self.zip_code}"
    
    def __str__(self) -> str:
        return f"Einsatz - {self.address()} [{self.label}]"
    
    def __repr__(self) -> str:
        return f"Einsatz - {self.address()} [{self.label}] >{self.status.value}<"
    

# =============================================================================
# MESSAGE MODEL
# =============================================================================

class Priority(str, Enum):
    low = 'Niedrig'
    medium = 'Mittel'
    high = 'Hoch'
    top = 'Blitz'
    
    
class Message(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    content: str
    prio: Priority = Priority.medium
    
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: User = Relationship(back_populates="messages")
    
    mission_id: int = Field(foreign_key="mission.id")
    mission: Mission = Relationship(back_populates="messages")
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    
# =============================================================================
# UNIT MODEL
# =============================================================================

UNIT_STATUS = {
    1: 'Einsatzbereit über Funk',
    2: 'Einsatzbereit auf Wache',
    3: 'Einsatz übernommen',
    4: 'Einsatzstelle an',
    5: 'Sprechwunsch',
    6: 'Nicht einsatzbereit',
    7: 'Patient aufgenommen',
    8: 'Am Transportziel',
    9: 'Notarzt aufgenommen',
    0: 'Notruf',
}
    
class Unit(SQLModel, table=True):
    label: str = Field(primary_key=True)
    status: int = 6
    status_prev: int | None = None
    comment: str | None = None
    
    vf: int = 0
    zf: int = 0
    gf: int = 0
    ms: int = 0
    agt: int = 0
    
    mission_id: int | None = Field(default=None, foreign_key="mission.id")
    mission: Mission = Relationship(back_populates="units")
    
    update: datetime = Field(default_factory=datetime.now)
