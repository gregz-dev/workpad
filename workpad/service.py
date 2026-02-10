from typing import List, Optional, Dict
from datetime import datetime, timezone

from .models import (
    Entry, EntryCreate, EntryUpdate, EntryFilter, 
    ContextItem, ContextItemCreate, 
    EntryType, EntryStatus
)
from .storage.base import StorageInterface
from .errors import NotFoundError, ValidationError

class WorkpadService:
    def __init__(self, storage: StorageInterface):
        self.storage = storage

    # --- CRUD Operations ---

    def create_entry(self, data: EntryCreate) -> Entry:
        """Create a new entry."""
        # Convert ContextItemCreate list to ContextItem list
        context_items = []
        if data.context_items:
            for item in data.context_items:
                context_items.append(ContextItem(
                    type=item.type,
                    source=item.source,
                    content=item.content,
                    metadata=item.metadata or {}
                ))

        entry = Entry(
            type=data.type,
            content=data.content,
            context_items=context_items,
            tags=data.tags or [],
            metadata=data.metadata or {}
        )
        
        return self.storage.create(entry)

    def get_entry(self, entry_id: str) -> Entry:
        """Get an entry by ID. Raises NotFoundError if not found."""
        entry = self.storage.get(entry_id)
        if not entry:
            raise NotFoundError(f"Entry {entry_id} not found")
        return entry

    def list_entries(self, filters: EntryFilter) -> List[Entry]:
        """List entries matching filters."""
        return self.storage.list(filters)

    def update_entry(self, entry_id: str, data: EntryUpdate) -> Entry:
        """Update an existing entry."""
        # Check existence (implicitly done by update usually, but let's be safe)
        if not self.storage.get(entry_id):
             raise NotFoundError(f"Entry {entry_id} not found")
        
        # Perfrom update via storage
        updated = self.storage.update(entry_id, data)
        if not updated:
            raise NotFoundError(f"Entry {entry_id} not found during update")
        
        return updated

    def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry."""
        if not self.storage.get(entry_id):
            raise NotFoundError(f"Entry {entry_id} not found")
        
        return self.storage.delete(entry_id)

    # --- Context Management ---

    def add_context(self, entry_id: str, data: ContextItemCreate) -> ContextItem:
        """Add a context item to an entry."""
        entry = self.get_entry(entry_id)
        
        new_item = ContextItem(
            type=data.type,
            source=data.source,
            content=data.content,
            metadata=data.metadata or {}
        )
        
        entry.context_items.append(new_item)
        
        # Persist using update
        self.storage.update(entry_id, EntryUpdate(context_items=entry.context_items))
        
        return new_item

    def remove_context(self, entry_id: str, context_id: str) -> bool:
        """Remove a context item from an entry."""
        entry = self.get_entry(entry_id)
        
        initial_count = len(entry.context_items)
        entry.context_items = [item for item in entry.context_items if item.id != context_id]
        
        if len(entry.context_items) == initial_count:
            return False # Context item not found
            
        self.storage.update(entry_id, EntryUpdate(context_items=entry.context_items))
        return True

    # --- Relations ---

    def add_relation(self, entry_id: str, related_id: str) -> bool:
        """Add a bidirectional relation between two entries."""
        if entry_id == related_id:
            raise ValidationError("Cannot link entry to itself")
            
        entry1 = self.get_entry(entry_id)
        entry2 = self.get_entry(related_id)
        
        updated1 = False
        updated2 = False

        if related_id not in entry1.related_entries:
            entry1.related_entries.append(related_id)
            updated1 = True
        
        if entry_id not in entry2.related_entries:
            entry2.related_entries.append(entry_id)
            updated2 = True
            
        if updated1:
            self.storage.update(entry_id, EntryUpdate(related_entries=entry1.related_entries))
        if updated2:
            self.storage.update(related_id, EntryUpdate(related_entries=entry2.related_entries))
        
        return True

    def remove_relation(self, entry_id: str, related_id: str) -> bool:
        """Remove a bidirectional relation."""
        entry1 = self.get_entry(entry_id)
        
        # We try to get entry2, but if it doesn't exist, we still clean up entry1
        try:
            entry2 = self.storage.get(related_id)
        except Exception:
            entry2 = None
            
        updated1 = False
        if related_id in entry1.related_entries:
            entry1.related_entries.remove(related_id)
            updated1 = True
            
        if updated1:
             self.storage.update(entry_id, EntryUpdate(related_entries=entry1.related_entries))

        if entry2:
            updated2 = False
            if entry_id in entry2.related_entries:
                entry2.related_entries.remove(entry_id)
                updated2 = True
            
            if updated2:
                self.storage.update(related_id, EntryUpdate(related_entries=entry2.related_entries))
            
        return True

    # --- Stats ---

    def get_stats(self) -> Dict:
        """Get statistics about entries."""
        # Using list with empty filter to get all index metadata (if implementation optimized)
        # JSONStorage implementation reads all metadata.json matches.
        all_entries = self.storage.list(EntryFilter())
        
        stats = {
            "total_entries": len(all_entries),
            "by_type": {},
            "by_status": {},
            "date_range": {"oldest": None, "newest": None}
        }
        
        if not all_entries:
            return stats
            
        timestamps = []
        for e in all_entries:
            t = e.type.value
            stats["by_type"][t] = stats["by_type"].get(t, 0) + 1
            
            s = e.status.value
            stats["by_status"][s] = stats["by_status"].get(s, 0) + 1
            
            timestamps.append(e.timestamp)
            
        if timestamps:
            stats["date_range"]["oldest"] = min(timestamps).isoformat()
            stats["date_range"]["newest"] = max(timestamps).isoformat()
            
        return stats
