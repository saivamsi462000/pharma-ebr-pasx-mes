"""Automated OQ test cases. Each test name carries the URS requirement ID it verifies
(see docs/validation/RTM.md)."""
import dataclasses
import sqlite3
from datetime import date

import pytest

from ebr import persistence
from ebr.engine import Batch, ExecutionError
from ebr.integration import SapEccGateway
from ebr.recipe import MasterRecipe, RecipeError
from ebr.security import AccessDenied, SignatureError
from run_demo import OP, QA, SUP, TODAY, build_environment

GOOD_DISPENSE = [
    {"material": "RM-API-500", "container_id": "C-0001", "net_kg": 100.0},
    {"material": "RM-MCC-101", "container_id": "C-0002", "net_kg": 14.4},
    {"material": "RM-PVP-K30", "container_id": "C-0003", "net_kg": 3.6},
    {"material": "RM-MGST-01", "container_id": "C-0004", "net_kg": 1.2},
    {"material": "RM-COAT-WH", "container_id": "C-0005", "net_kg": 0.8},
]


@pytest.fixture
def env():
    audit, users, equipment, inventory, lims = build_environment()
    return {"audit": audit, "users": users, "equipment": equipment, "inventory": inventory,
            "lims": lims, "sap": SapEccGateway(), "recipe": MasterRecipe.load("recipes/MBR-TAB-500.json")}


def new_batch(env, recipe=None):
    order = {"order_no": "PO-1", "material": "FG-100500", "batch": "B260302",
             "planned_qty": 200000, "mbr_id": "MBR-TAB-500"}
    b = Batch(order, recipe or env["recipe"], env["users"], env["audit"], env["sap"],
              env["lims"], env["equipment"], env["inventory"])
    b.start(OP[0])
    return b


def to_dispense(b, dispenses=GOOD_DISPENSE):
    b.execute_phase("0010-01", OP, SUP)
    b.execute_phase("0010-02", OP, data={"today": TODAY})
    return b.execute_phase("0010-03", OP, SUP, data={"today": TODAY, "dispenses": dispenses})


def run_to_end(b, hardness=14.0):
    to_dispense(b)
    b.execute_phase("0020-01", OP, data={"today": TODAY})
    for pid, v in [("0020-02", 150), ("0020-03", 12.0)]:
        b.execute_phase(pid, OP, value=v)
    b.execute_phase("0020-04", OP, SUP, value=2.0)
    b.execute_phase("0030-01", OP, value=15)
    b.execute_phase("0030-02", OP, SUP)
    b.execute_phase("0030-03", OP)
    b.execute_phase("0040-01", OP, value=600)
    b.execute_phase("0040-02", OP, value=hardness)
    if b.status == "ON_HOLD":
        return b
    b.execute_phase("0040-03", OP, value=18)
    b.execute_phase("0050-01", OP, value=42)
    b.execute_phase("0050-02", OP, SUP, value=3.0)
    b.execute_phase("0060-01", OP, SUP)
    b.execute_phase("0060-02", OP, SUP, data={"good_units": 196000})
    return b


# --- Recipe management ---------------------------------------------------------
def test_URS_01_only_approved_mbr_can_create_batch(env):
    draft = dataclasses.replace(env["recipe"], status="Draft")
    with pytest.raises(RecipeError):
        new_batch(env, draft)


def test_URS_02_mbr_validation_rejects_bad_limits(env):
    bad = env["recipe"].phases[5]
    broken = dataclasses.replace(bad, spec={**bad.spec, "low": 200, "high": 100})
    recipe = dataclasses.replace(env["recipe"], phases=(broken,) + env["recipe"].phases[1:])
    with pytest.raises(RecipeError):
        recipe.validate()


# --- Execution control ---------------------------------------------------------
def test_URS_03_phases_cannot_be_skipped(env):
    b = new_batch(env)
    with pytest.raises(ExecutionError, match="Out of sequence"):
        b.execute_phase("0020-02", OP, value=150)


def test_URS_04_dirty_equipment_blocks_execution(env):
    env["equipment"]["BAL-150KG-02"].clean_status = "Dirty"
    b = new_batch(env)
    b.execute_phase("0010-01", OP, SUP)
    with pytest.raises(ExecutionError, match="cleaning required"):
        b.execute_phase("0010-02", OP, data={"today": TODAY})


def test_URS_04_expired_calibration_blocks_execution(env):
    env["equipment"]["BAL-150KG-02"].calibration_due = date(2026, 1, 1)
    b = new_batch(env)
    b.execute_phase("0010-01", OP, SUP)
    with pytest.raises(ExecutionError, match="calibration expired"):
        b.execute_phase("0010-02", OP, data={"today": TODAY})


# --- Material control ----------------------------------------------------------
def test_URS_05_wrong_material_scan_rejected(env):
    bad = [dict(d) for d in GOOD_DISPENSE]
    bad[1]["container_id"] = "C-0001"  # API container scanned for MCC
    with pytest.raises(ExecutionError, match="Scan mismatch"):
        to_dispense(new_batch(env), bad)


def test_URS_05_quarantined_container_rejected(env):
    bad = [dict(d) for d in GOOD_DISPENSE]
    bad[0]["container_id"] = "C-0099"
    with pytest.raises(ExecutionError, match="Quarantine"):
        to_dispense(new_batch(env), bad)


def test_URS_06_weight_outside_tolerance_rejected(env):
    bad = [dict(d) for d in GOOD_DISPENSE]
    bad[0]["net_kg"] = 101.0  # tolerance is ±0.5 kg
    with pytest.raises(ExecutionError, match="re-weigh"):
        to_dispense(new_batch(env), bad)


# --- Exceptions, hold & release -----------------------------------------------
def test_URS_07_out_of_limit_value_creates_exception(env):
    b = new_batch(env)
    to_dispense(b)
    b.execute_phase("0020-01", OP, data={"today": TODAY})
    b.execute_phase("0020-02", OP, value=171)  # CPP limit 160
    assert b.exceptions[0].severity == "Major" and b.status == "IN_EXECUTION"


def test_URS_08_cqa_excursion_puts_batch_on_hold(env):
    b = run_to_end(new_batch(env), hardness=8.0)
    assert b.status == "ON_HOLD"
    with pytest.raises(ExecutionError, match="ON_HOLD"):
        b.execute_phase("0040-03", OP, value=18)


def test_URS_09_major_exception_requires_deviation(env):
    b = run_to_end(new_batch(env), hardness=8.0)
    b.comment_exception("EXC-B260302-01", SUP, "investigating")
    with pytest.raises(ExecutionError, match="deviation"):
        b.qa_close_exception("EXC-B260302-01", QA)


def test_URS_10_release_blocked_with_open_exception(env):
    b = new_batch(env)
    run_to_end(b)
    b._raise_exception(b.recipe.phases[-1], "manual test exception")
    b.submit_for_review(SUP[0])
    with pytest.raises(ExecutionError, match="open exceptions"):
        b.qa_disposition(QA, "RELEASED")


def test_URS_11_happy_path_release_and_sap_messages(env):
    b = run_to_end(new_batch(env))
    b.submit_for_review(SUP[0])
    b.qa_disposition(QA, "RELEASED")
    types = [m["msg_type"] for m in env["sap"].outbox]
    assert b.status == "RELEASED"
    assert types.count("GOODS_ISSUE") == 5 and "GOODS_RECEIPT" in types and types[-1] == "USAGE_DECISION"
    assert types.count("CONFIRMATION") == 6  # one per operation


# --- Part 11: signatures, access, audit trail --------------------------------
def test_URS_12_performer_and_verifier_must_differ(env):
    b = new_batch(env)
    with pytest.raises(ExecutionError, match="different people"):
        b.execute_phase("0010-01", SUP, SUP)


def test_URS_12_verification_required(env):
    b = new_batch(env)
    with pytest.raises(ExecutionError, match="second-person"):
        b.execute_phase("0010-01", OP)


def test_URS_13_wrong_pin_rejected_and_account_locked(env):
    b = new_batch(env)
    for _ in range(3):
        with pytest.raises(SignatureError):
            b.execute_phase("0010-01", ("op.jsmith", "0000"), SUP)
    with pytest.raises(AccessDenied):
        b.execute_phase("0010-01", OP, SUP)
    assert any(a.action == "ACCOUNT_LOCKED" for a in env["audit"].entries)


def test_URS_14_operator_cannot_release_batch(env):
    b = run_to_end(new_batch(env))
    b.submit_for_review(SUP[0])
    with pytest.raises(AccessDenied):
        b.qa_disposition(OP, "RELEASED")


def test_URS_14_admin_has_no_gmp_execution_rights(env):
    assert not env["users"].get("adm.mes").can("execute_phase")
    assert not env["users"].get("adm.mes").can("release_batch")


def test_URS_15_audit_trail_detects_tampering(env):
    b = run_to_end(new_batch(env))
    audit = env["audit"]
    assert audit.verify()
    audit._entries[10] = dataclasses.replace(audit._entries[10], new_value="999")
    assert not audit.verify()


def test_URS_15_signature_manifest_contents(env):
    rec = to_dispense(new_batch(env))
    m = rec.signatures[0].manifest()
    assert "J. Smith" in m and "Performed by" in m and "T" in m  # name, meaning, timestamp


def test_URS_16_database_audit_trail_is_append_only(env):
    b = run_to_end(new_batch(env))
    con = persistence.connect()
    persistence.save(con, b)
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        con.execute("UPDATE audit_trail SET user_id = 'x' WHERE seq = 1")
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        con.execute("DELETE FROM audit_trail")


def test_URS_17_backward_and_forward_genealogy(env):
    b = run_to_end(new_batch(env))
    con = persistence.connect()
    persistence.save(con, b)
    q = persistence.queries()
    back = con.execute(q["backward_genealogy"], {"batch_id": "B260302"}).fetchall()
    fwd = con.execute(q["forward_genealogy"], {"lot": "L-API-2601"}).fetchall()
    assert len(back) == 5 and fwd[0][1] == "B260302"
