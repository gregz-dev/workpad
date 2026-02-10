import uuid
from datetime import datetime, timezone

def generate_uuid() -> str:
    """Generate a UUID4 string."""
    return str(uuid.uuid4())

def now_utc() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)

def format_iso(dt: datetime) -> str:
    """Format datetime to ISO 8601 string."""
    return dt.isoformat()
