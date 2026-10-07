# 21 CFR Part 11 / EU Annex 11 Compliance Matrix

| Clause | Requirement | How it is met | Evidence |
|---|---|---|---|
| §11.10(a) | Validation of systems | URS → FS → DS → RTM → IQ/OQ/PQ; automated OQ suite | `docs/validation/*`, `pytest -v` |
| §11.10(b) | Accurate and complete copies | RBE and full EBR exports (Markdown), CSV audit trail, SQL tables | `output/` |
| §11.10(c) | Record protection and retention | Append-only DB triggers; controlled backups (procedural) | `sql/schema.sql` |
| §11.10(d) | Limit system access to authorised individuals | RBAC; inactive / locked accounts denied | `ebr/security.py` |
| §11.10(e) | Secure, time-stamped audit trail | UTC timestamps, user, old/new value, reason; SHA-256 hash chain | `ebr/audit.py` |
| §11.10(f) | Operational system checks (sequencing) | Enforced phase sequence and status machine | `Batch.execute_phase` |
| §11.10(g) | Authority checks | Permission check on every action and signature | `UserDirectory.require` |
| §11.10(h) | Device checks | Equipment ID / status and container scan validation | `_do_equipment_check`, `_do_weigh_dispense` |
| §11.10(i) | Training of users | Procedural (SOP training records) | SOP-EBR-001 |
| §11.10(k) | Control of system documentation | Git version control; change control | `Change_Control_Template.md` |
| §11.50 | Signature manifestation | Printed name, date/time, meaning on every signature | `ESignature.manifest()` |
| §11.70 | Signature / record linking | Signature object bound to `record_id`; immutable | `ESignature` (frozen) |
| §11.100 | Uniqueness of e-signatures | One user ID per person; IDs never reassigned (procedural) | User directory |
| §11.200(a) | Two-component signature (ID + password) | User ID + PIN re-entered at every signing | `UserDirectory.sign` |
| §11.300 | Controls for identification codes / passwords | Salted PBKDF2 hashes; lockout after 3 failures | `ebr/security.py` |
| Annex 11 §9 | Audit trails reviewed | Integrity status printed on the RBE report | `review_by_exception` |
| Annex 11 §12 | Security | Segregation of duties: admin has no GMP rights | `PERMISSIONS` |

## ALCOA+ mapping

| Principle | Control |
|---|---|
| **A**ttributable | Every entry carries a user ID; e-signatures |
| **L**egible | Structured records and human-readable reports |
| **C**ontemporaneous | System-generated UTC timestamp at the time of action |
| **O**riginal | First capture stored; no overwrite path |
| **A**ccurate | Limit checks, scan checks, tolerance checks |
| Complete / Consistent / Enduring / Available | Hash chain, append-only storage, SQL queries for retrieval |
