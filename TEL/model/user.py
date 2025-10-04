from datetime import datetime
from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field

# =============================================================================
# DATABASE MODEL
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
