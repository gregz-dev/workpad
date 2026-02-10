from typing import List, Optional, Dict
from datetime import datetime, timezone
import json

from sqlmodel import SQLModel, Field, Session, create_engine, select, Relationship
from sqlalchemy import JSON 

from ..models import (
    Entry, EntryCreate, EntryUpdate, EntryFilter, 
    ContextItem, EntryType, EntryStatus, ContextType
)
from ..storage.base import StorageInterface
from ..errors import StorageError, NotFoundError

# --- DB Models ---

class EntryTable(SQLModel, table=True):
    __tablename__ = "entries"

    id: str = Field(primary_key=True)
    type: str # Store enum as string
    content: str
    status: str
    timestamp: datetime
    created_at: datetime
    updated_at: datetime
    tags_json: str = Field(default="[]") # Store list of strings as JSON
    metadata_json: str = Field(default="{}")
    related_entries_json: str = Field(default="[]")

    # Relationships
    context_items: List["ContextItemTable"] = Relationship(back_populates="entry", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class ContextItemTable(SQLModel, table=True):
    __tablename__ = "context_items"

    id: str = Field(primary_key=True)
    entry_id: str = Field(foreign_key="entries.id")
    type: str
    source: str
    content: str
    metadata_json: str = Field(default="{}")
    created_at: datetime

    entry: EntryTable = Relationship(back_populates="context_items")

# --- Implementation ---

class SQLiteStorage(StorageInterface):
    def __init__(self, db_path: str):
        # Allow in-memory for tests or file path
        if db_path == ":memory:":
            self.db_url = "sqlite://" 
        else:
            self.db_url = f"sqlite:///{db_path}/workpad.db"
        
        # We delay engine creation to initialize? No, usually in init.
        # But initialize() method is expected by interface.
        self.engine = None

    def initialize(self) -> None:
        try:
            self.engine = create_engine(self.db_url)
            SQLModel.metadata.create_all(self.engine)
        except Exception as e:
            raise StorageError(f"Failed to initialize SQLite storage: {e}")

    def _to_domain(self, db_entry: EntryTable) -> Entry:
        context_items = [
            ContextItem(
                id=c.id,
                type=ContextType(c.type),
                source=c.source,
                content=c.content,
                metadata=json.loads(c.metadata_json),
                created_at=c.created_at.replace(tzinfo=timezone.utc) if c.created_at.tzinfo is None else c.created_at
            ) for c in db_entry.context_items
        ]

        return Entry(
            id=db_entry.id,
            type=EntryType(db_entry.type),
            content=db_entry.content,
            status=EntryStatus(db_entry.status),
            timestamp=db_entry.timestamp.replace(tzinfo=timezone.utc) if db_entry.timestamp.tzinfo is None else db_entry.timestamp,
            created_at=db_entry.created_at.replace(tzinfo=timezone.utc) if db_entry.created_at.tzinfo is None else db_entry.created_at,
            updated_at=db_entry.updated_at.replace(tzinfo=timezone.utc) if db_entry.updated_at.tzinfo is None else db_entry.updated_at,
            tags=json.loads(db_entry.tags_json),
            metadata=json.loads(db_entry.metadata_json),
            related_entries=json.loads(db_entry.related_entries_json),
            context_items=context_items
        )

    def create(self, entry: Entry) -> Entry:
        try:
            db_entry = EntryTable(
                id=entry.id,
                type=entry.type.value,
                content=entry.content,
                status=entry.status.value,
                timestamp=entry.timestamp,
                created_at=entry.created_at,
                updated_at=entry.updated_at,
                tags_json=json.dumps(entry.tags),
                metadata_json=json.dumps(entry.metadata),
                related_entries_json=json.dumps(entry.related_entries)
            )
            
            # Context items
            for c in entry.context_items:
                db_context = ContextItemTable(
                    id=c.id,
                    entry_id=entry.id,
                    type=c.type.value,
                    source=c.source,
                    content=c.content,
                    metadata_json=json.dumps(c.metadata),
                    created_at=c.created_at
                )
                db_entry.context_items.append(db_context)

            with Session(self.engine) as session:
                session.add(db_entry)
                session.commit()
                session.refresh(db_entry)
                return self._to_domain(db_entry)
        except Exception as e:
            raise StorageError(f"Failed to create entry: {e}")

    def get(self, entry_id: str) -> Optional[Entry]:
        try:
            with Session(self.engine) as session:
                db_entry = session.get(EntryTable, entry_id)
                if not db_entry:
                    return None
                return self._to_domain(db_entry)
        except Exception as e:
            raise StorageError(f"Failed to get entry: {e}")

    def list(self, filters: EntryFilter) -> List[Entry]:
        try:
            statement = select(EntryTable)
            
            if filters.type:
                statement = statement.where(EntryTable.type == filters.type.value)
            if filters.status:
                statement = statement.where(EntryTable.status == filters.status.value)
            if filters.from_date:
                statement = statement.where(EntryTable.timestamp >= filters.from_date)
            if filters.to_date:
                statement = statement.where(EntryTable.timestamp <= filters.to_date)
            if filters.search:
                statement = statement.where(EntryTable.content.contains(filters.search))
                
            # Tags filter is tricky with JSON string storage in SQLite
            # Simple mostly-working approach: LIKE '%"tag"%'
            if filters.tags:
                for tag in filters.tags:
                    statement = statement.where(EntryTable.tags_json.contains(f'"{tag}"'))

            # Sort desc
            statement = statement.order_by(EntryTable.timestamp.desc())
            
            # Pagination
            statement = statement.offset(filters.offset).limit(filters.limit)

            with Session(self.engine) as session:
                results = session.exec(statement).all()
                return [self._to_domain(e) for e in results]
        except Exception as e:
            raise StorageError(f"Failed to list entries: {e}")

    def update(self, entry_id: str, updates: EntryUpdate) -> Optional[Entry]:
        try:
            with Session(self.engine) as session:
                db_entry = session.get(EntryTable, entry_id)
                if not db_entry:
                    return None

                if updates.content is not None:
                    db_entry.content = updates.content
                if updates.type is not None:
                    db_entry.type = updates.type.value
                if updates.status is not None:
                    db_entry.status = updates.status.value
                if updates.tags is not None:
                    db_entry.tags_json = json.dumps(updates.tags)
                if updates.metadata is not None:
                    # Merge metadata
                    current = json.loads(db_entry.metadata_json)
                    current.update(updates.metadata)
                    db_entry.metadata_json = json.dumps(current)
                if updates.related_entries is not None:
                    db_entry.related_entries_json = json.dumps(updates.related_entries)
                
                # Context items update (replace all if provided? Or merge?)
                # Service implementation for remove_context/add_context updates the WHOLE list on entry
                # and calls update(context_items=...).
                # So we should replace the list.
                if updates.context_items is not None:
                    # Strategy: Delete all existing and re-add new ones. 
                    # This is simple and effective for this domain (context items are usually part of the entry).
                    # Since we use cascade delete, we can clear the list.
                    # Use session.exec to delete existing items for this entry
                    # (Though simply assigning new list *might* work depending on configuration, explicit delete is safer)
                    
                    # First, remove associations or delete items. 
                    # For cascade delete-orphan, removing from list should suffice IF loaded.
                    # But db_entry.context_items might be lazy loaded.
                    # Let's try clearing the list on the object.
                    db_entry.context_items = []
                    
                    # Create new items
                    for c in updates.context_items:
                        new_item = ContextItemTable(
                            id=c.id,
                            entry_id=entry_id,
                            type=c.type.value,
                            source=c.source,
                            content=c.content,
                            metadata_json=json.dumps(c.metadata),
                            created_at=c.created_at
                        )
                        db_entry.context_items.append(new_item)

                db_entry.updated_at = datetime.now(timezone.utc)
                session.add(db_entry)
                session.commit()
                session.refresh(db_entry)
                return self._to_domain(db_entry)
        except Exception as e:
            raise StorageError(f"Failed to update entry: {e}")

    def delete(self, entry_id: str) -> bool:
        try:
            with Session(self.engine) as session:
                db_entry = session.get(EntryTable, entry_id)
                if not db_entry:
                    return False
                session.delete(db_entry)
                session.commit()
                return True
        except Exception as e:
            raise StorageError(f"Failed to delete entry: {e}")
