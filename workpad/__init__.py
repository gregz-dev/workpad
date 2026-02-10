"""
Workpad - Generic note/entry management system.
"""

__version__ = "0.1.0"

from .service import WorkpadService
from .storage.json_storage import JSONStorage
from .models import Entry, EntryType, EntryStatus
