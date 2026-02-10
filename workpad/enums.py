from enum import Enum

class EntryType(str, Enum):
    observation = "observation"
    hypothesis = "hypothesis"
    test = "test"
    nextstep = "nextstep"
    note = "note"
    task = "task"

class EntryStatus(str, Enum):
    active = "active"
    completed = "completed"
    invalidated = "invalidated"
    confirmed = "confirmed"
    archived = "archived"

class ContextType(str, Enum):
    code_snippet = "code_snippet"
    file = "file"
    stacktrace = "stacktrace"
    log_excerpt = "log_excerpt"
    url = "url"
    commit = "commit"
    note = "note"
