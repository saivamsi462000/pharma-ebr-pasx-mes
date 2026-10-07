"""Electronic Batch Record (EBR) execution engine.

Batch lifecycle:

    CREATED -> IN_EXECUTION <-> ON_HOLD -> EXECUTED -> UNDER_REVIEW -> RELEASED | REJECTED

Rules enforced (each is traced to a requirement in docs/validation/RTM.md):
* Only an Approved master recipe can create a batch.
* Phases run in the sequence defined by the MBR; nothing can be skipped.
* Equipment must be Clean and in calibration; containers must be Released, unexpired
  and match the expected material (scan verification).
* Dispensed weights must be within the BOM tolerance.
* Values outside limits raise an exception. A CQA excursion puts the batch ON HOLD.
* Steps flagged performer_verifier need two different people to sign.
* A batch cannot be released while any exception is still open.
"""
from dataclasses import dataclass, field
from datetime import date, timedelta

from ebr.audit import AuditTrail, utc_now
from ebr.integration import Container, Equipment, LimsStub, SapEccGateway, zebra_label
from ebr.recipe import MasterRecipe, Phase
from ebr.security import ESignature, UserDirectory


class ExecutionError(Exception):
    pass


SEVERITY = {"CQA": "Major", "CPP": "Major", "KPI": "Minor", None: "Minor"}


@dataclass
class BatchException:
    exc_id: str
    phase_id: str
    description: str
    criticality: str | None
    severity: str
    value: float | None = None
    low: float | None = None
    high: float | None = None
    status: str = "Open"           # Open -> Commented -> Closed
    comment: str | None = None
    deviation_no: str | None = None
    signatures: list[ESignature] = field(default_factory=list)


@dataclass
class PhaseRecord:
    phase: Phase
    status: str = "Pending"        # Pending -> Completed
    value: float | None = None
    data: dict = field(default_factory=dict)
    signatures: list[ESignature] = field(default_factory=list)
    completed_at: str | None = None


class Batch:
    def __init__(self, order: dict, recipe: MasterRecipe, users: UserDirectory, audit: AuditTrail,
                 sap: SapEccGateway, lims: LimsStub, equipment: dict[str, Equipment],
                 inventory: dict[str, Container]):
        recipe.require_approved()
        self.order = SapEccGateway.receive_production_order(order)
        if order["mbr_id"] != recipe.mbr_id:
            raise ExecutionError("Production order references a different MBR")
        self.batch_id = order["batch"]
        self.recipe, self.users, self.audit = recipe, users, audit
        self.sap, self.lims, self.equipment, self.inventory = sap, lims, equipment, inventory
        self.records = [PhaseRecord(p) for p in recipe.phases]
        self.exceptions: list[BatchException] = []
        self.consumption: list[dict] = []
        self.status = "CREATED"
        self.release_signatures: list[ESignature] = []
        self.audit.record("system", "BATCH_CREATED", self.batch_id,
                          new_value=f"{recipe.mbr_id} v{recipe.version} / order {order['order_no']}")

    # ------------------------------------------------------------------ helpers
    def _set_status(self, new: str, user: str, reason: str | None = None) -> None:
        self.audit.record(user, "STATUS_CHANGE", self.batch_id, self.status, new, reason)
        self.status = new

    def next_phase(self) -> PhaseRecord | None:
        return next((r for r in self.records if r.status == "Pending"), None)

    def _record(self, phase_id: str) -> PhaseRecord:
        rec = next((r for r in self.records if r.phase.phase_id == phase_id), None)
        if rec is None:
            raise ExecutionError(f"Unknown phase {phase_id}")
        return rec

    def _raise_exception(self, phase: Phase, description: str, value=None) -> BatchException:
        crit = phase.spec.get("criticality")
        exc = BatchException(f"EXC-{self.batch_id}-{len(self.exceptions) + 1:02d}", phase.phase_id,
                             description, crit, SEVERITY.get(crit, "Minor"), value,
                             phase.spec.get("low"), phase.spec.get("high"))
        self.exceptions.append(exc)
        self.audit.record("system", "EXCEPTION_RAISED", exc.exc_id, new_value=description)
        if crit == "CQA":
            self._set_status("ON_HOLD", "system", f"CQA excursion {exc.exc_id}")
        return exc

    # ---------------------------------------------------------------- execution
    def start(self, user_id: str) -> None:
        self.users.require(user_id, "execute_phase")
        if self.status != "CREATED":
            raise ExecutionError("Batch already started")
        self._set_status("IN_EXECUTION", user_id)

    def execute_phase(self, phase_id: str, performer: tuple[str, str],
                      verifier: tuple[str, str] | None = None,
                      value: float | None = None, data: dict | None = None) -> PhaseRecord:
        if self.status != "IN_EXECUTION":
            raise ExecutionError(f"Batch is {self.status}; execution not allowed")
        rec = self._record(phase_id)
        expected = self.next_phase()
        if rec is not expected:
            raise ExecutionError(f"Out of sequence: expected {expected.phase.phase_id}, got {phase_id}")
        phase, data = rec.phase, data or {}

        # Signatures first: re-authentication failures must not leave partial data
        sigs = [self.users.sign(*performer, "sign_performer", "Performed by", phase_id)]
        if phase.signature == "performer_verifier":
            if not verifier:
                raise ExecutionError(f"{phase_id} requires a second-person verification")
            if verifier[0] == performer[0]:
                raise ExecutionError("Performer and verifier must be different people")
            sigs.append(self.users.sign(*verifier, "sign_verifier", "Verified by", phase_id))

        handler = getattr(self, f"_do_{phase.type}")
        value = handler(phase, value, data)

        if phase.has_limits and value is not None and not (phase.spec["low"] <= value <= phase.spec["high"]):
            self._raise_exception(
                phase, f"{phase.spec.get('parameter', phase.type)} = {value} outside "
                       f"[{phase.spec['low']}, {phase.spec['high']}]", value)

        rec.value, rec.data, rec.signatures = value, data, sigs
        rec.status, rec.completed_at = "Completed", utc_now()
        self.audit.record(performer[0], "PHASE_COMPLETED", phase_id, new_value=value)

        last_of_op = all(r.status == "Completed" for r in self.records if r.phase.op_id == phase.op_id)
        if last_of_op:
            self.sap.confirmation(self.order["order_no"], phase.op_id)
        if self.next_phase() is None and self.status == "IN_EXECUTION":
            self._set_status("EXECUTED", performer[0])
        return rec

    # phase handlers -------------------------------------------------------
    def _do_line_clearance(self, phase, value, data):
        return None

    def _do_equipment_check(self, phase, value, data):
        today = data.get("today", date.today())
        for eq_id in phase.spec["equipment"]:
            eq = self.equipment.get(eq_id)
            if eq is None:
                raise ExecutionError(f"Equipment {eq_id} not found in equipment master")
            if eq.clean_status != "Clean":
                raise ExecutionError(f"{eq_id} status is {eq.clean_status}; cleaning required")
            if eq.calibration_due < today:
                raise ExecutionError(f"{eq_id} calibration expired on {eq.calibration_due}")
        return None

    def _do_weigh_dispense(self, phase, value, data):
        today = data.get("today", date.today())
        dispensed = {d["material"]: d for d in data["dispenses"]}
        for material in phase.spec["materials"]:
            d = dispensed.get(material)
            if d is None:
                raise ExecutionError(f"Material {material} was not dispensed")
            cont = self.inventory.get(d["container_id"])
            if cont is None or cont.material != material:
                raise ExecutionError(f"Scan mismatch: container {d['container_id']} is not {material}")
            if cont.status != "Released":
                raise ExecutionError(f"Container {cont.container_id} is {cont.status}")
            if cont.expiry < today:
                raise ExecutionError(f"Container {cont.container_id} expired {cont.expiry}")
            bom = self.recipe.bom[material]
            tol = bom["qty_kg"] * bom["tolerance_pct"] / 100
            if abs(d["net_kg"] - bom["qty_kg"]) > tol:
                raise ExecutionError(
                    f"{material}: {d['net_kg']} kg outside {bom['qty_kg']} ± {tol:.3f} kg; re-weigh required")
            self.consumption.append({"material": material, "lot": cont.lot,
                                     "container_id": cont.container_id, "qty_kg": d["net_kg"]})
            self.sap.goods_issue(self.order["order_no"], material, cont.lot, d["net_kg"])
            self.audit.record("system", "MATERIAL_CONSUMED", cont.container_id, new_value=d["net_kg"])
        return None

    def _do_process_parameter(self, phase, value, data):
        if value is None:
            raise ExecutionError(f"{phase.phase_id}: value required")
        return value

    def _do_sampling(self, phase, value, data):
        data["sample_id"] = self.lims.create_sample(self.batch_id, phase.spec["lims_test"], phase.phase_id)
        return None

    def _do_lims_result(self, phase, value, data):
        sample = next(r["sample_id"] for r in reversed(self.lims.requests))
        data["sample_id"] = sample
        return self.lims.get_result(sample)

    def _do_label_print(self, phase, value, data):
        expiry = data.get("expiry", date.today() + timedelta(days=730))
        data["zpl"] = zebra_label(self.batch_id, self.recipe.product["material"],
                                  self.recipe.product["description"], expiry, data.get("gtin", "00312345678906"))
        return None

    def _do_yield(self, phase, value, data):
        good = data["good_units"]
        theoretical = self.recipe.product["theoretical_yield_tablets"]
        data["theoretical"] = theoretical
        self.sap.goods_receipt(self.order["order_no"], self.recipe.product["material"], self.batch_id, good)
        return round(100 * good / theoretical, 2)

    # ------------------------------------------------------- exceptions & QA
    def comment_exception(self, exc_id: str, user: tuple[str, str], comment: str,
                          deviation_no: str | None = None) -> None:
        exc = self._exc(exc_id)
        sig = self.users.sign(*user, "comment_exception", "Exception commented", exc_id)
        exc.comment, exc.deviation_no, exc.status = comment, deviation_no, "Commented"
        exc.signatures.append(sig)
        self.audit.record(user[0], "EXCEPTION_COMMENTED", exc_id, new_value=comment)

    def qa_close_exception(self, exc_id: str, qa: tuple[str, str]) -> None:
        exc = self._exc(exc_id)
        if exc.status != "Commented":
            raise ExecutionError("Exception must be commented before QA closure")
        if exc.severity == "Major" and not exc.deviation_no:
            raise ExecutionError("Major exceptions require a linked deviation number")
        exc.signatures.append(self.users.sign(*qa, "approve_exception", "Approved by QA", exc_id))
        exc.status = "Closed"
        self.audit.record(qa[0], "EXCEPTION_CLOSED", exc_id)

    def qa_lift_hold(self, qa: tuple[str, str], reason: str) -> None:
        if self.status != "ON_HOLD":
            raise ExecutionError("Batch is not on hold")
        self.users.sign(*qa, "hold_batch", "Hold lifted by QA", self.batch_id)
        self._set_status("IN_EXECUTION" if self.next_phase() else "EXECUTED", qa[0], reason)

    def submit_for_review(self, user_id: str) -> None:
        if self.status != "EXECUTED":
            raise ExecutionError(f"Batch is {self.status}; must be EXECUTED")
        self._set_status("UNDER_REVIEW", user_id)

    def qa_disposition(self, qa: tuple[str, str], decision: str) -> None:
        if self.status != "UNDER_REVIEW":
            raise ExecutionError("Batch must be UNDER_REVIEW")
        open_exc = [e.exc_id for e in self.exceptions if e.status != "Closed"]
        if decision == "RELEASED" and open_exc:
            raise ExecutionError(f"Cannot release with open exceptions: {open_exc}")
        meaning = "Released by QA" if decision == "RELEASED" else "Rejected by QA"
        self.release_signatures.append(self.users.sign(*qa, "release_batch", meaning, self.batch_id))
        self.sap.usage_decision(self.batch_id, "A" if decision == "RELEASED" else "R")
        self._set_status(decision, qa[0])

    def _exc(self, exc_id: str) -> BatchException:
        try:
            return next(e for e in self.exceptions if e.exc_id == exc_id)
        except StopIteration:
            raise ExecutionError(f"Unknown exception {exc_id}") from None

    # ------------------------------------------------------- reconciliation
    def material_reconciliation(self) -> list[dict]:
        rows = []
        for material, bom in self.recipe.bom.items():
            issued = sum(c["qty_kg"] for c in self.consumption if c["material"] == material)
            rows.append({"material": material, "bom_kg": bom["qty_kg"], "issued_kg": round(issued, 3),
                         "variance_pct": round(100 * (issued - bom["qty_kg"]) / bom["qty_kg"], 3)})
        return rows
