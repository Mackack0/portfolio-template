from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Esquemas para los proyectos
class ProjectBase(BaseModel):
    project_id: str
    title: str
    short_desc: str
    long_desc: str
    tech: List[str]
    image: str
    link: str

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    short_desc: Optional[str] = None
    long_desc: Optional[str] = None
    tech: Optional[List[str]] = None
    image: Optional[str] = None
    link: Optional[str] = None

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Esquemas para la información personal
class PersonalInfoBase(BaseModel):
    name: str
    title: str
    bio: str
    short_bio: str
    stack: List[str]
    tools: List[str]
    university: str
    location: str

class PersonalInfoCreate(PersonalInfoBase):
    pass

class PersonalInfoUpdate(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    bio: Optional[str] = None
    short_bio: Optional[str] = None
    stack: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    university: Optional[str] = None
    location: Optional[str] = None

class PersonalInfo(PersonalInfoBase):
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Esquemas para los mensajes de contacto
class ContactMessageBase(BaseModel):
    name: str
    email: str
    message: str

class ContactMessageCreate(ContactMessageBase):
    pass

class ContactMessage(ContactMessageBase):
    id: int
    created_at: datetime
    read: int
    
    class Config:
        from_attributes = True

# Autenticación admin
class AdminLogin(BaseModel):
    password: str
