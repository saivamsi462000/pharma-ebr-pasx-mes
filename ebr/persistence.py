"""Persist a batch to SQL and run the traceability queries."""
import re
import sqlite3
from pathlib import Path

from ebr.engine import Batch

ROOT = Path(__file__).resolve().parent.parent


def connect(path: str = ":memory:") -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.executescript((ROOT / "sql/schema.sql").read_text())
    return con


def save(con: sqlite3.Connection, batch: Batch) -> None:
    r = batch.recipe
    con.execute("INSERT INTO batch VALUES (?,?,?,?,?,?)",
                (batch.batch_id, batch.order["order_no"], r.product["material"], r.mbr_id, r.version, batch.status))
    for rec in batch.records:
        p = rec.phase
        con.execute("INSERT INTO phase_record VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (batch.batch_id, p.phase_id, p.op_name, p.type, p.spec.get("parameter"), rec.value,
                     p.spec.get("low"), p.spec.get("high"), p.spec.get("criticality"), rec.completed_at))
        for s in rec.signatures:
            con.execute("INSERT INTO e_signature (record_id, batch_id, user_id, printed_name, meaning, signed_at) "
                        "VALUES (?,?,?,?,?,?)", (s.record_id, batch.batch_id, s.user_id, s.printed_name,
                                                  s.meaning, s.timestamp))
    for e in batch.exceptions:
        con.execute("INSERT INTO batch_exception VALUES (?,?,?,?,?,?,?,?)",
                    (e.exc_id, batch.batch_id, e.phase_id, e.description, e.criticality, e.severity,
                     e.deviation_no, e.status))
        for s in e.signatures:
            con.execute("INSERT INTO e_signature (record_id, batch_id, user_id, printed_name, meaning, signed_at) "
                        "VALUES (?,?,?,?,?,?)", (s.record_id, batch.batch_id, s.user_id, s.printed_name,
                                                  s.meaning, s.timestamp))
    for c in batch.consumption:
        con.execute("INSERT INTO material_consumption VALUES (?,?,?,?,?)",
                    (batch.batch_id, c["material"], c["lot"], c["container_id"], c["qty_kg"]))
    for a in batch.audit.entries:
        con.execute("INSERT OR IGNORE INTO audit_trail VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (a.seq, a.timestamp, a.user, a.action, a.object_id, a.old_value, a.new_value,
                     a.reason, a.prev_hash, a.hash))
    con.commit()


def queries() -> dict[str, str]:
    text = (ROOT / "sql/traceability_queries.sql").read_text()
    parts = re.split(r"^-- name: (\w+)\s*$", text, flags=re.M)
    return {parts[i]: parts[i + 1].strip().rstrip(";") for i in range(1, len(parts), 2)}
