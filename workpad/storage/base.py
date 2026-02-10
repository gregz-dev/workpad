from abc import ABC, abstractmethod
from typing import List, Optional

from ..models import Entry, EntryFilter, EntryUpdate

class StorageInterface(ABC):
    """Abstract interface for storage backends."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the storage (create directories, tables, etc)."""
        pass

    @abstractmethod
    def create(self, entry: Entry) -> Entry:
        """Persist a new entry."""
        pass

    @abstractmethod
    def get(self, entry_id: str) -> Optional[Entry]:
        """Retrieve an entry by ID."""
        pass

    @abstractmethod
    def list(self, filters: EntryFilter) -> List[Entry]:
        """List entries matching filters."""
        pass

    @abstractmethod
    def update(self, entry_id: str, updates: EntryUpdate) -> Optional[Entry]:
        """Update an existing entry."""
        pass
    
    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        """Delete an entry."""
        pass
