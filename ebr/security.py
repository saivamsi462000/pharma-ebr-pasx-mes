"""Role-based access control and electronic signatures (21 CFR Part 11 §11.50, §11.100, §11.200).

* Each user has exactly one role; permissions are granted to roles, never to users.
* Signing requires re-authentication (user ID + PIN) at the moment of signing.
* A signature manifest shows printed name, date/time and meaning (§11.50).
* Signatures are linked to the record they sign and cannot be copied (§11.70).
* Performer and verifier of the same step must be different people (four-eyes principle).
"""
import hashlib
import hmac
import os
from dataclasses import dataclass

from ebr.audit import AuditTrail, utc_now

PERMISSIONS = {
    "Operator": {"execute_phase", "sign_performer"},
    "Supervisor": {"execute_phase", "sign_performer", "sign_verifier", "comment_exception"},
    "QA Reviewer": {"sign_verifier", "review_batch", "approve_exception", "release_batch", "hold_batch"},
    "MES Admin": {"manage_users", "manage_recipes"},  # deliberately no GMP execution rights
}


class AccessDenied(Exception):
    pass


class SignatureError(Exception):
    pass


@dataclass
class User:
    user_id: str
    full_name: str
    role: str
    _salt: bytes
    _pin_hash: bytes
    active: bool = True

    def can(self, permission: str) -> bool:
        return self.active and permission in PERMISSIONS[self.role]


@dataclass(frozen=True)
class ESignature:
    user_id: str
    printed_name: str
    meaning: str          # e.g. "Performed by", "Verified by", "Approved by QA"
    timestamp: str
    record_id: str

    def manifest(self) -> str:
        return f"{self.printed_name} ({self.user_id}) | {self.meaning} | {self.timestamp}"


class UserDirectory:
    MAX_FAILED = 3

    def __init__(self, audit: AuditTrail):
        self.audit = audit
        self._users: dict[str, User] = {}
        self._failed: dict[str, int] = {}

    def add_user(self, user_id: str, full_name: str, role: str, pin: str) -> None:
        if role not in PERMISSIONS:
            raise ValueError(f"Unknown role {role}")
        salt = os.urandom(16)
        self._users[user_id] = User(user_id, full_name, role, salt, self._hash(pin, salt))
        self.audit.record("system", "USER_CREATED", user_id, new_value=role)

    @staticmethod
    def _hash(pin: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 100_000)

    def get(self, user_id: str) -> User:
        return self._users[user_id]

    def require(self, user_id: str, permission: str) -> User:
        user = self._users.get(user_id)
        if not user or not user.can(permission):
            self.audit.record(user_id, "ACCESS_DENIED", permission)
            raise AccessDenied(f"{user_id} lacks permission '{permission}'")
        return user

    def sign(self, user_id: str, pin: str, permission: str, meaning: str, record_id: str) -> ESignature:
        user = self.require(user_id, permission)
        if not hmac.compare_digest(self._hash(pin, user._salt), user._pin_hash):
            self._failed[user_id] = self._failed.get(user_id, 0) + 1
            self.audit.record(user_id, "SIGNATURE_FAILED", record_id)
            if self._failed[user_id] >= self.MAX_FAILED:
                user.active = False
                self.audit.record("system", "ACCOUNT_LOCKED", user_id, reason="3 failed signature attempts")
            raise SignatureError("Re-authentication failed")
        self._failed[user_id] = 0
        sig = ESignature(user_id, user.full_name, meaning, utc_now(), record_id)
        self.audit.record(user_id, "E_SIGNATURE", record_id, new_value=meaning)
        return sig
