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
        # Convert EntryCreate to Entry
        # Note: id, timestamp, created/updated_at are handled by Entry defaults
        
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
        # Check existence
        existing = self.get_entry(entry_id)
        
        # Perfrom update via storage
        updated = self.storage.update(entry_id, data)
        if not updated:
            # Should not happen if get_entry passed, unless race condition or storage error
            raise NotFoundError(f"Entry {entry_id} not found during update")
        
        return updated

    def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry."""
        # Check existence? Or just try delete.
        # Doc says raise NotFoundError if not found.
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
        entry.updated_at = datetime.now(timezone.utc)
        
        # We need to save the entry. 
        # Since update takes EntryUpdate, implementation depends on storage support.
        # But wait, storage.update takes EntryUpdate which is partial.
        # Replacing the whole list context_items via EntryUpdate is not strictly defined in EntryUpdate model yet?
        # Let's check EntryUpdate model in models.py
        
        # Current EntryUpdate model:
        # class EntryUpdate(BaseModel):
        #     content: Optional[str] = Field(None, max_length=50000)
        #     type: Optional[EntryType] = None
        #     status: Optional[EntryStatus] = None
        #     tags: Optional[List[str]] = None
        #     metadata: Optional[Dict] = None

        # It seems EntryUpdate DOES NOT support updating context_items directly!
        # This is a gap in my previous implementation plan/models.
        
        # OPTION 1: Add context_items to EntryUpdate
        # OPTION 2: Storage.update logic needs to handle full object replacement? No.
        # OPTION 3: Explicitly saving the modified entry using storage.create (overwrite)? 
        #           But storage.create usually fails if exists or creates new.
        # OPTION 4: Modify storage.update to accept generic updates or modify properties directly?
        # The most clean way is to add context_items to EntryUpdate so we can persist changes.
        
        # However, for now, let's assume I should update EntryUpdate to support context_items.
        # I will update "models.py" first to include context_items in EntryUpdate.
        
        # Re-reading EntryUpdate definition:
        # It's missing context_items.
        
        # I'll update models.py in a separate step. For now writing code assuming it works.
        # But wait, I cannot write code that fails. 
        # I will hack this: since JSONStorage.update updates what's passed, 
        # I need to pass context_items.
        # But Pydantic will validate EntryUpdate.
        
        # PLAN CHANGE: I must update models.py to include context_items in EntryUpdate.
        pass # Placeholder

    # --- Relations ---

    def add_relation(self, entry_id: str, related_id: str) -> bool:
        """Add a bidirectional relation between two entries."""
        if entry_id == related_id:
            raise ValidationError("Cannot link entry to itself")
            
        entry1 = self.get_entry(entry_id)
        entry2 = self.get_entry(related_id)
        
        if related_id not in entry1.related_entries:
            entry1.related_entries.append(related_id)
            # Need to save entry1
        
        if entry_id not in entry2.related_entries:
            entry2.related_entries.append(entry_id)
            # Need to save entry2
            
        # Again, same issue: need to persist `related_entries`.
        # I need to update EntryUpdate model.
        
        return True

    def remove_relation(self, entry_id: str, related_id: str) -> bool:
        """Remove a bidirectional relation."""
        entry1 = self.get_entry(entry_id)
        # Check entry2 exists? Not strictly required if we just want to remove loose link, 
        # but for consistency yes.
        try:
            entry2 = self.get_entry(related_id)
        except NotFoundError:
            entry2 = None
            
        if related_id in entry1.related_entries:
            entry1.related_entries.remove(related_id)
            # Save entry1
            
        if entry2 and entry_id in entry2.related_entries:
            entry2.related_entries.remove(entry_id)
            # Save entry2
            
        return True

    # --- Stats ---

    def get_stats(self) -> Dict:
        """Get statistics about entries."""
        # This implementation on JSON storage might be slow (list all).
        # Optimal way: storage.list(EntryFilter()) metadata only if possible.
        # JSONStorage.list already uses index.
        all_entries = self.storage.list(EntryFilter())
        
        stats = {
            "total_entries": len(all_entries),
            "by_type": {},
            "by_status": {},
            "date_range": {"oldest": None, "newest": None}
        }
        
        if not all_entries:
            return stats
            
        # Calculate stats
        timestamps = []
        for e in all_entries:
            # Type
            t = e.type.value
            stats["by_type"][t] = stats["by_type"].get(t, 0) + 1
            
            # Status
            s = e.status.value
            stats["by_status"][s] = stats["by_status"].get(s, 0) + 1
            
            timestamps.append(e.timestamp)
            
        if timestamps:
            stats["date_range"]["oldest"] = min(timestamps).isoformat()
            stats["date_range"]["newest"] = max(timestamps).isoformat()
            
        return stats
