"""End-to-end demo: SAP order -> EBR execution with two excursions -> QA review -> release.

Usage:
    python run_demo.py
Outputs are written to ./output/.
"""
import json
from datetime import date
from pathlib import Path

from ebr import persistence
from ebr.audit import AuditTrail
from ebr.engine import Batch
from ebr.integration import Container, Equipment, LimsStub, SapEccGateway
from ebr.recipe import MasterRecipe
from ebr.review import full_batch_record, review_by_exception
from ebr.security import UserDirectory

OUT = Path("output")
TODAY = date(2026, 3, 2)

# Demo-only PINs for fictitious users. Not real credentials.
OP = ("op.jsmith", "1111")
SUP = ("sup.rpatel", "3333")
QA = ("qa.kchen", "4444")


def build_environment():
    audit = AuditTrail()
    users = UserDirectory(audit)
    users.add_user("op.jsmith", "J. Smith", "Operator", "1111")
    users.add_user("op.mlee", "M. Lee", "Operator", "2222")
    users.add_user("sup.rpatel", "R. Patel", "Supervisor", "3333")
    users.add_user("qa.kchen", "K. Chen", "QA Reviewer", "4444")
    users.add_user("adm.mes", "MES Admin", "MES Admin", "9999")

    equipment = {eq: Equipment(eq, "Clean", date(2026, 12, 31))
                 for eq in ["BOOTH-01", "BAL-150KG-02", "HSG-300"]}
    inventory = {
        "C-0001": Container("C-0001", "RM-API-500", "L-API-2601", "Released", date(2027, 6, 30)),
        "C-0002": Container("C-0002", "RM-MCC-101", "L-MCC-2588", "Released", date(2027, 1, 31)),
        "C-0003": Container("C-0003", "RM-PVP-K30", "L-PVP-2542", "Released", date(2026, 11, 30)),
        "C-0004": Container("C-0004", "RM-MGST-01", "L-MGS-2519", "Released", date(2027, 3, 31)),
        "C-0005": Container("C-0005", "RM-COAT-WH", "L-CWH-2607", "Released", date(2026, 9, 30)),
        "C-0099": Container("C-0099", "RM-API-500", "L-API-2499", "Quarantine", date(2027, 6, 30)),
    }
    lims = LimsStub({"SMP-B260302-001": 2.8})
    return audit, users, equipment, inventory, lims


def main() -> None:
    OUT.mkdir(exist_ok=True)
    audit, users, equipment, inventory, lims = build_environment()
    sap = SapEccGateway()
    recipe = MasterRecipe.load("recipes/MBR-TAB-500.json")

    order = {"order_no": "PO-1000452", "material": "FG-100500", "batch": "B260302",
             "planned_qty": 200000, "mbr_id": "MBR-TAB-500"}
    b = Batch(order, recipe, users, audit, sap, lims, equipment, inventory)
    b.start(OP[0])

    # Dispensing
    b.execute_phase("0010-01", OP, SUP)
    b.execute_phase("0010-02", OP, data={"today": TODAY})
    b.execute_phase("0010-03", OP, SUP, data={"today": TODAY, "dispenses": [
        {"material": "RM-API-500", "container_id": "C-0001", "net_kg": 100.12},
        {"material": "RM-MCC-101", "container_id": "C-0002", "net_kg": 14.38},
        {"material": "RM-PVP-K30", "container_id": "C-0003", "net_kg": 3.61},
        {"material": "RM-MGST-01", "container_id": "C-0004", "net_kg": 1.21},
        {"material": "RM-COAT-WH", "container_id": "C-0005", "net_kg": 0.80},
    ]})
    # Granulation
    b.execute_phase("0020-01", OP, data={"today": TODAY})
    b.execute_phase("0020-02", OP, value=152)
    b.execute_phase("0020-03", OP, value=12.4)
    b.execute_phase("0020-04", OP, SUP, value=1.8)
    # Blending
    b.execute_phase("0030-01", OP, value=15)
    b.execute_phase("0030-02", OP, SUP)
    b.execute_phase("0030-03", OP)                        # LIMS returns RSD 2.8%
    # Compression: hardness CQA excursion -> batch goes ON HOLD
    b.execute_phase("0040-01", OP, value=601.5)
    b.execute_phase("0040-02", OP, value=9.4)
    print(f"After hardness IPC: batch status = {b.status}")
    b.comment_exception("EXC-B260302-01", SUP,
                        "Press tooling wear found; punches replaced, 20-tablet re-test mean 13.8 kp",
                        deviation_no="DEV-2026-0117")
    b.qa_close_exception("EXC-B260302-01", QA)
    b.qa_lift_hold(QA, "DEV-2026-0117 assessed; product impact none after tooling change")
    b.execute_phase("0040-03", OP, value=18.6)
    # Coating: exhaust temperature CPP excursion (major, no hold)
    b.execute_phase("0050-01", OP, value=46.8)
    b.execute_phase("0050-02", OP, SUP, value=3.1)
    # Packaging
    b.execute_phase("0060-01", OP, SUP, data={"expiry": date(2028, 3, 31)})
    b.execute_phase("0060-02", OP, SUP, data={"good_units": 195_210})

    b.comment_exception("EXC-B260302-02", SUP,
                        "Transient 0.8 °C excursion for 2 min during spray-rate ramp; within PAR per validation report",
                        deviation_no="DEV-2026-0118")
    b.qa_close_exception("EXC-B260302-02", QA)
    b.submit_for_review(SUP[0])
    b.qa_disposition(QA, "RELEASED")

    # Outputs
    (OUT / "review_by_exception.md").write_text(review_by_exception(b))
    (OUT / "electronic_batch_record.md").write_text(full_batch_record(b))
    (OUT / "sap_outbox.json").write_text(json.dumps(sap.outbox, indent=2))
    (OUT / "shipper_label.zpl").write_text(b._record("0060-01").data["zpl"])
    (OUT / "audit_trail.csv").write_text(
        "seq,timestamp,user,action,object_id,old_value,new_value,reason,hash\n" + "\n".join(
            f'{a.seq},{a.timestamp},{a.user},{a.action},{a.object_id},"{a.old_value or ""}",'
            f'"{a.new_value or ""}","{a.reason or ""}",{a.hash[:16]}' for a in audit.entries))

    con = persistence.connect()
    persistence.save(con, b)
    q = persistence.queries()
    genealogy = con.execute(q["backward_genealogy"], {"batch_id": b.batch_id}).fetchall()

    print(f"Final status      : {b.status}")
    print(f"Exceptions        : {len(b.exceptions)} (all closed: {all(e.status == 'Closed' for e in b.exceptions)})")
    print(f"Yield             : {b._record('0060-02').value}%")
    print(f"SAP messages sent : {len(sap.outbox)} -> " + ", ".join(sorted({m['msg_type'] for m in sap.outbox})))
    print(f"Audit entries     : {len(audit.entries)} (chain verified: {audit.verify()})")
    print(f"Genealogy rows    : {len(genealogy)}")
    print(f"Outputs written to {OUT}/")


if __name__ == "__main__":
    main()
