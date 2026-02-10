from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator

from .enums import EntryType, EntryStatus, ContextType
from .utils import generate_uuid, now_utc

class ContextItem(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    type: ContextType
    source: str
    content: str = Field(max_length=100000)
    metadata: Dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=now_utc)

class ContextItemCreate(BaseModel):
    type: ContextType
    source: str
    content: str = Field(max_length=100000)
    metadata: Optional[Dict] = Field(default_factory=dict)

class Entry(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    timestamp: datetime = Field(default_factory=now_utc)
    type: EntryType
    content: str = Field(max_length=50000)
    context_items: List[ContextItem] = Field(default_factory=list)
    status: EntryStatus = Field(default=EntryStatus.active)
    related_entries: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list, max_length=20)
    metadata: Dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=now_utc)
    updated_at: datetime = Field(default_factory=now_utc)

    @field_validator('tags')
    def validate_tags(cls, v):
        for tag in v:
            if len(tag) > 50:
                raise ValueError("Tag length must be <= 50 chars")
        return v

class EntryCreate(BaseModel):
    type: EntryType
    content: str = Field(max_length=50000)
    context_items: Optional[List[ContextItemCreate]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None

class EntryUpdate(BaseModel):
    content: Optional[str] = Field(None, max_length=50000)
    type: Optional[EntryType] = None
    status: Optional[EntryStatus] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict] = None

class EntryFilter(BaseModel):
    type: Optional[EntryType] = None
    status: Optional[EntryStatus] = None
    tags: Optional[List[str]] = None
    search: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
