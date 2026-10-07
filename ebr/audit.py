"""Tamper-evident audit trail (21 CFR Part 11 §11.10(e)).

Every GxP-relevant action is appended as an immutable entry. Each entry stores the
SHA-256 hash of the previous entry, so any edit, deletion or reordering breaks the
chain and is detected by `verify()`.
"""
import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class AuditEntry:
    seq: int
    timestamp: str
    user: str
    action: str
    object_id: str
    old_value: str | None
    new_value: str | None
    reason: str | None
    prev_hash: str
    hash: str = field(default="")

    def payload(self) -> str:
        d = asdict(self)
        d.pop("hash")
        return json.dumps(d, sort_keys=True)


class AuditTrail:
    GENESIS = "0" * 64

    def __init__(self):
        self._entries: list[AuditEntry] = []

    def record(self, user: str, action: str, object_id: str, old_value=None,
               new_value=None, reason: str | None = None) -> AuditEntry:
        prev = self._entries[-1].hash if self._entries else self.GENESIS
        draft = AuditEntry(len(self._entries) + 1, utc_now(), user, action, object_id,
                           None if old_value is None else str(old_value),
                           None if new_value is None else str(new_value), reason, prev)
        entry = AuditEntry(**{**asdict(draft), "hash": hashlib.sha256(draft.payload().encode()).hexdigest()})
        self._entries.append(entry)
        return entry

    @property
    def entries(self) -> tuple[AuditEntry, ...]:
        return tuple(self._entries)  # read-only view: no update/delete API exists

    def verify(self) -> bool:
        prev = self.GENESIS
        for e in self._entries:
            if e.prev_hash != prev or hashlib.sha256(e.payload().encode()).hexdigest() != e.hash:
                return False
            prev = e.hash
        return True
