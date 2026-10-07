"""Confirmed, append-only memories with explicit correction/evolution links.

Original JSON files are never edited. All cooperating writers use a directory
lock; a lock left by a terminated writer requires manual inspection, not an
automatic unlock. No current-state retrieval or authorization is implemented.
"""

import json
import os
import tempfile
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4


PROJECT_DIR = Path(__file__).resolve().parent
MEMORIES_DIR = PROJECT_DIR / "data" / "memories"


def _check_storage_path():
    """Reject a data directory redirected outside this project."""
    if not MEMORIES_DIR.resolve().is_relative_to(PROJECT_DIR):
        raise ValueError("Memory storage must remain inside the project directory.")


def _validate_fields(content, tags, source, user_confirmed):
    if user_confirmed is not True:
        raise ValueError("Memory must be explicitly confirmed by the user.")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Content must be a non-empty string.")
    if not isinstance(source, str) or not source.strip():
        raise ValueError("Source must be a non-empty string.")
    if not isinstance(tags, list) or any(
        not isinstance(tag, str) or not tag.strip() for tag in tags
    ):
        raise ValueError("Tags must be a list of non-empty strings (or an empty list).")


def _validate_id(memory_id):
    if not isinstance(memory_id, str):
        raise ValueError("Memory ID must be a canonical UUID string.")
    try:
        valid_id = str(UUID(memory_id))
    except ValueError as error:
        raise ValueError("Memory ID must be a canonical UUID string.") from error
    if valid_id != memory_id:
        raise ValueError("Memory ID must be a canonical UUID string.")


def _validate_date(value):
    if value is None:
        return
    if not isinstance(value, str):
        raise ValueError("effective_from must be YYYY-MM-DD or None.")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("effective_from must be a valid YYYY-MM-DD date.") from error
    if parsed.isoformat() != value:
        raise ValueError("effective_from must use exactly YYYY-MM-DD.")


@contextmanager
def _writer_lock():
    """Serialize relation checks and publication across cooperating processes."""
    _check_storage_path()
    MEMORIES_DIR.mkdir(parents=True, exist_ok=True)
    lock_path = MEMORIES_DIR / ".memory-store.lock"
    # Exclusive creation: never remove another writer's existing lock.
    handle = lock_path.open("x", encoding="utf-8")
    try:
        with handle:
            handle.write(str(os.getpid()))
        yield
    finally:
        lock_path.unlink()


def _write_record(record):
    """Publish complete JSON with replace, under _writer_lock, without overwrite.

    The lock makes the existence check and replace safe among Store writers.
    External programs editing the directory are outside this coordination.
    Temporary files are not JSON candidates and are removed on handled errors.
    """
    text = json.dumps(record, ensure_ascii=False, indent=2) + "\n"
    text.encode("utf-8")
    _validate_id(record["id"])
    path = MEMORIES_DIR / (record["id"] + ".json")
    if os.path.lexists(path):
        raise FileExistsError(f"Memory ID already exists: {record['id']}")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=MEMORIES_DIR,
            prefix=".memory-", suffix=".tmp", delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        if os.path.lexists(path):
            raise FileExistsError(f"Memory ID already exists: {record['id']}")
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _new_record(content, tags, source, user_confirmed):
    _validate_fields(content, tags, source, user_confirmed)
    return {
        "schema_version": 1,
        "id": str(uuid4()),
        "content": content,
        "tags": list(tags),
        "source": source,
        "user_confirmed": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def save_memory(content, tags, source, *, user_confirmed, effective_from=None):
    """Save a new UTF-8 JSON record and return it; never overwrite a file.

    The caller must pass the actual boolean True after explicit user confirmation.
    This flag records confirmation; it does not authenticate a user.
    """
    _validate_date(effective_from)
    record = _new_record(content, tags, source, user_confirmed)
    if effective_from is not None:
        record["effective_from"] = effective_from
    with _writer_lock():
        _write_record(record)
    return record


def _validate_relationship(record):
    relation = record.get("relationship_type")
    previous = record.get("previous_memory_id")
    _validate_date(record.get("effective_from"))
    if relation in (None, ""):
        if previous not in (None, ""):
            raise ValueError("A previous ID requires correction or evolution.")
        return
    if relation not in ("correction", "evolution"):
        raise ValueError("relationship_type must be correction or evolution.")
    _validate_id(previous)
    if previous == record["id"]:
        raise ValueError("A memory cannot reference itself.")
    if relation == "evolution" and record.get("effective_from") is None:
        raise ValueError("Evolution requires an explicit effective_from date.")


def _validate_links(records):
    successors = {}
    for record in records.values():
        if record.get("relationship_type") not in ("correction", "evolution"):
            continue
        previous_id = record["previous_memory_id"]
        if previous_id not in records:
            raise ValueError(f"Missing previous memory: {previous_id}")
        if previous_id in successors:
            raise ValueError("A previous memory already has a successor.")
        successors[previous_id] = record["id"]
        previous_date = records[previous_id].get("effective_from")
        if record["relationship_type"] == "correction":
            if record.get("effective_from") != previous_date:
                raise ValueError("Correction must inherit the previous effective_from.")
        elif previous_date is not None and record["effective_from"] <= previous_date:
            raise ValueError("Evolution must take effect after the previous state.")
    complete = set()
    for memory_id in records:
        trail = set()
        current = memory_id
        while current is not None and current not in complete:
            if current in trail:
                raise ValueError("Cyclic memory relationships are not allowed.")
            trail.add(current)
            current = records[current].get("previous_memory_id") or None
        complete.update(trail)


def update_memory(previous_memory_id, content, tags, source, *,
                  relationship_type, user_confirmed, effective_from=None):
    """Append an explicitly confirmed correction/evolution, never edit its parent.

    Correction inherits the parent's date (possibly unknown); callers must not
    supply a date. Evolution requires a user-supplied date. Only one successor
    per parent is allowed; update the latest record instead of branching.
    """
    _validate_id(previous_memory_id)
    if relationship_type not in ("correction", "evolution"):
        raise ValueError("relationship_type must be correction or evolution.")
    _validate_date(effective_from)
    if relationship_type == "correction" and effective_from is not None:
        raise ValueError("Correction inherits its date; do not supply effective_from.")
    if relationship_type == "evolution" and effective_from is None:
        raise ValueError("Evolution requires an explicit effective_from date.")
    record = _new_record(content, tags, source, user_confirmed)
    with _writer_lock():
        records = {path.stem: load_memory(path.stem)
                   for path in sorted(MEMORIES_DIR.glob("*.json"))}
        _validate_links(records)
        if previous_memory_id not in records:
            raise ValueError(f"Missing previous memory: {previous_memory_id}")
        if record["id"] in records:
            raise FileExistsError(f"Memory ID already exists: {record['id']}")
        record.update({
            "relationship_type": relationship_type,
            "previous_memory_id": previous_memory_id,
            "effective_from": (records[previous_memory_id].get("effective_from")
                               if relationship_type == "correction" else effective_from),
        })
        _validate_relationship(record)
        _validate_links({**records, record["id"]: record})
        _write_record(record)
    return record


def load_memory(memory_id):
    """Read one record from disk by its canonical UUID; reject malformed records.

    Missing files, invalid JSON and I/O errors are reported to the caller.
    """
    _validate_id(memory_id)
    _check_storage_path()
    path = MEMORIES_DIR / (memory_id + ".json")
    if not path.resolve().is_relative_to(MEMORIES_DIR.resolve()):
        raise ValueError("Memory file must remain inside the memory directory.")
    with path.open("r", encoding="utf-8") as handle:
        record = json.load(handle)
    if not isinstance(record, dict):
        raise ValueError("Memory record must be a JSON object.")
    if type(record.get("schema_version")) is not int or record["schema_version"] != 1:
        raise ValueError("Unsupported memory schema version.")
    if record.get("id") != memory_id:
        raise ValueError("Memory record ID does not match its filename.")
    _validate_fields(
        record.get("content"), record.get("tags"), record.get("source"),
        record.get("user_confirmed"),
    )
    created_at = record.get("created_at")
    if not isinstance(created_at, str):
        raise ValueError("Creation time must be an ISO 8601 string with a timezone.")
    try:
        timestamp = datetime.fromisoformat(created_at)
    except ValueError as error:
        raise ValueError("Invalid creation time.") from error
    if timestamp.utcoffset() is None:
        raise ValueError("Creation time must include a timezone.")
    _validate_relationship(record)
    return record
