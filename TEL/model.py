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
    admin = 'admin'
    
    
class UserInfo(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    name: str
    email: str
    permission: Permission | None = None
    

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
        
    changed_at: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    
    messages: List["Message"] = Relationship(back_populates="mission")
    
    def __str__(self):
        if self.street_no:
            return f"Einsatz {self.label} - {' '.join([self.street, self.street_no])}, {self.zip_code}"
        return f"Einsatz {self.label} - {self.street, self.street_no}, {self.zip_code}"
    
    def __repr__(self):
        if self.street_no:
            return f"Einsatz {self.label} - {self.category.value} - {' '.join([self.street, self.street_no])}, {self.zip_code} [{self.status.value}]"
        return f"Einsatz {self.label} - {self.category.value} - {self.street}, {self.zip_code} [{self.status.value}]"
    

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
    
    user_name: Optional[str] = None
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: User = Relationship(back_populates="messages")
    
    mission_id: int = Field(foreign_key="mission.id")
    mission: Mission = Relationship(back_populates="messages")
    
    created_at: datetime = Field(default_factory=datetime.now)