"""
Database Schemas for Hacksters Portfolio

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name (e.g., TeamMember -> "teammember").

These schemas are consumed by the backend endpoints for validation and by tools
that introspect the /schema endpoint.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, EmailStr

# ---------------------------
# Organization / Site Content
# ---------------------------
class Organization(BaseModel):
    name: str = Field(..., description="Organization name")
    founded_year: int = Field(..., description="Year founded")
    mission: str = Field(..., description="Mission statement")
    description: Optional[str] = Field(None, description="Longer description")
    logo_url: Optional[HttpUrl] = Field(None, description="Logo URL")
    socials: dict = Field(default_factory=dict, description="Map of social links")

class Stats(BaseModel):
    patents: int = Field(0, ge=0, description="Patents filed")
    team_size: int = Field(0, ge=0, description="Current team size")
    achievements: int = Field(0, ge=0, description="Major achievements count")

# ---------
# Timeline
# ---------
EventType = Literal["win", "participated"]

class Event(BaseModel):
    title: str = Field(..., description="Event name")
    date: str = Field(..., description="Date string, e.g., 2023-11-01")
    venue: str = Field(..., description="Venue / Location")
    type: EventType = Field(..., description="win or participated")
    position: Optional[str] = Field(None, description="1st, 2nd, 3rd, Champion, etc. When type=win")
    description: Optional[str] = Field(None, description="Short description")
    photos: List[HttpUrl] = Field(default_factory=list, description="Event photo URLs")

# -------------
# Team Members
# -------------
class TeamMember(BaseModel):
    name: str = Field(..., description="Full name")
    role: str = Field(..., description="Role / Title")
    nickname: Optional[str] = Field(None, description="Display name")
    bio: Optional[str] = Field(None, description="Short bio")
    skills: List[str] = Field(default_factory=list, description="Skill tags")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    photo_url: Optional[HttpUrl] = Field(None, description="Headshot URL")
    instagram: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None

# ---------
# Contact
# ---------
class ContactSubmission(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
    company: Optional[str] = None

# Note: The Flames database viewer will automatically read these from /schema
