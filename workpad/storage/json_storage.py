import json
import os
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime, timezone

from ..models import Entry, EntryFilter, EntryUpdate
from ..errors import StorageError, NotFoundError
from .base import StorageInterface

class JSONStorage(StorageInterface):
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.entries_path = self.data_path / "entries"
        self.index_path = self.data_path / "metadata.json"
        self._index: Dict[str, dict] = {}

    def initialize(self) -> None:
        try:
            self.entries_path.mkdir(parents=True, exist_ok=True)
            if self.index_path.exists():
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    self._index = json.load(f)
            else:
                self._index = {}
                self._save_index()
        except Exception as e:
            raise StorageError(f"Failed to initialize storage: {e}")

    def _save_index(self):
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self._index, f, indent=2)
    
    def _get_entry_path(self, entry_id: str) -> Path:
        # We could shard by date, but for now simple flat structure or yyyy-mm as per doc
        # Doc suggested yyyy-mm. Let's try to look up date in index or just search?
        # If we have index, we can store relative path there.
        # But if we create, we need to decide where to put it.
        # Let's check index first.
        meta = self._index.get(entry_id)
        if meta and 'path' in meta:
            return self.data_path / meta['path']
        
        # Fallback search if not in index (should not happen if consistent)
        matches = list(self.entries_path.rglob(f"{entry_id}.json"))
        if matches:
            return matches[0]
        return None

    def create(self, entry: Entry) -> Entry:
        try:
            # Determine path: entries/YYYY-MM/uuid.json
            ym = entry.timestamp.strftime("%Y-%m")
            folder = self.entries_path / ym
            folder.mkdir(parents=True, exist_ok=True)
            
            file_path = folder / f"{entry.id}.json"
            
            # Save file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(entry.model_dump_json(indent=2))
            
            # Update index
            rel_path = file_path.relative_to(self.data_path)
            self._index[entry.id] = {
                "path": str(rel_path),
                "timestamp": entry.timestamp.isoformat(),
                "type": entry.type.value,
                "status": entry.status.value,
                "tags": entry.tags
            }
            self._save_index()
            return entry
        except Exception as e:
            raise StorageError(f"Failed to create entry: {e}")

    def get(self, entry_id: str) -> Optional[Entry]:
        path = self._get_entry_path(entry_id)
        if not path or not path.exists():
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = f.read()
                return Entry.model_validate_json(data)
        except Exception as e:
            raise StorageError(f"Failed to read entry {entry_id}: {e}")

    def list(self, filters: EntryFilter) -> List[Entry]:
        results = []
        # First filter by index to avoid reading all files
        candidates = []
        for eid, meta in self._index.items():
            # Apply filters on metadata
            if filters.type and meta['type'] != filters.type.value:
                continue
            if filters.status and meta['status'] != filters.status.value:
                continue
            if filters.tags:
                if not any(tag in meta['tags'] for tag in filters.tags):
                   continue
            # Date filter
            dt = datetime.fromisoformat(meta['timestamp'])
            if filters.from_date and dt < filters.from_date:
                continue
            if filters.to_date and dt > filters.to_date:
                continue
            
            candidates.append(eid)
        
        # Sort by timestamp desc
        candidates.sort(key=lambda x: self._index[x]['timestamp'], reverse=True)
        
        # Pagination - optimization: apply offset/limit on candidates
        # BUT search requires reading content.
        
        if filters.search:
            # If search is requested, we must read files.
            # We can still use the filtered candidates list as a starting point.
            matched_entries = []
            for eid in candidates:
                entry = self.get(eid)
                if entry and filters.search.lower() in entry.content.lower():
                    matched_entries.append(entry)
            
            # Now apply pagination on matched_entries
            start = filters.offset
            end = filters.offset + filters.limit
            return matched_entries[start:end]
        else:
            # No search, just apply pagination on candidates and load them
            start = filters.offset
            end = filters.offset + filters.limit
            paginated_ids = candidates[start:end]
            
            entries = []
            for eid in paginated_ids:
                entry = self.get(eid)
                if entry:
                    entries.append(entry)
            return entries

    def update(self, entry_id: str, updates: EntryUpdate) -> Optional[Entry]:
        entry = self.get(entry_id)
        if not entry:
            return None
        
        # Apply updates
        updated = False
        if updates.content is not None:
            entry.content = updates.content
            updated = True
        if updates.type is not None:
            entry.type = updates.type
            updated = True
        if updates.status is not None:
            entry.status = updates.status
            updated = True
        if updates.tags is not None:
            entry.tags = updates.tags
            updated = True
        if updates.metadata is not None:
            entry.metadata.update(updates.metadata)
            updated = True
        if updates.context_items is not None:
            entry.context_items = updates.context_items
            updated = True
        if updates.related_entries is not None:
            entry.related_entries = updates.related_entries
            updated = True
            
        if updated:
            entry.updated_at = datetime.now(timezone.utc) # Should use utc now
            # re-save
            try:
                path = self._get_entry_path(entry_id)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(entry.model_dump_json(indent=2))
                
                # Update index
                self._index[entry.id]['type'] = entry.type.value
                self._index[entry.id]['status'] = entry.status.value
                self._index[entry.id]['tags'] = entry.tags
                self._save_index()
            except Exception as e:
                raise StorageError(f"Failed to update entry: {e}")
                
        return entry

    def delete(self, entry_id: str) -> bool:
        path = self._get_entry_path(entry_id)
        if not path or not path.exists():
            return False
        
        try:
            path.unlink()
            if entry_id in self._index:
                del self._index[entry_id]
                self._save_index()
            return True
        except Exception as e:
            raise StorageError(f"Failed to delete entry: {e}")
