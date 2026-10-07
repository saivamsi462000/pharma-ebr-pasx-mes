"""Simulated interfaces to SAP ECC, LIMS, the equipment master and Zebra printers.

In a real deployment these are PAS-X interface adapters (SAP via IDoc/RFC or a
middleware layer; LIMS and others via REST/SOAP). Here each is a small in-memory
stub that keeps the same message semantics so the EBR flow can be shown end to end.
"""
from dataclasses import dataclass, field
from datetime import date

from ebr.audit import utc_now


@dataclass
class SapEccGateway:
    """Inbound production orders; outbound goods movements, confirmations and usage decisions."""
    outbox: list[dict] = field(default_factory=list)

    @staticmethod
    def receive_production_order(msg: dict) -> dict:
        required = {"order_no", "material", "batch", "planned_qty", "mbr_id"}
        missing = required - msg.keys()
        if missing:
            raise ValueError(f"Production order rejected, missing {sorted(missing)}")
        return msg

    def _send(self, msg_type: str, **payload) -> dict:
        msg = {"msg_type": msg_type, "sent_at": utc_now(), **payload}
        self.outbox.append(msg)
        return msg

    def goods_issue(self, order_no, material, batch, qty_kg):
        return self._send("GOODS_ISSUE", movement_type="261", order_no=order_no,
                          material=material, batch=batch, qty=qty_kg, uom="KG")

    def confirmation(self, order_no, operation, yield_qty=None):
        return self._send("CONFIRMATION", order_no=order_no, operation=operation, yield_qty=yield_qty)

    def goods_receipt(self, order_no, material, batch, qty):
        return self._send("GOODS_RECEIPT", movement_type="101", order_no=order_no,
                          material=material, batch=batch, qty=qty, uom="EA", stock_type="QI")

    def usage_decision(self, batch, decision):
        return self._send("USAGE_DECISION", batch=batch, decision=decision)


@dataclass
class Container:
    container_id: str
    material: str
    lot: str
    status: str          # Released / Quarantine / Rejected
    expiry: date


@dataclass
class Equipment:
    equipment_id: str
    clean_status: str    # Clean / Dirty
    calibration_due: date


class LimsStub:
    def __init__(self, results: dict[str, float] | None = None):
        self.results = results or {}
        self.requests: list[dict] = []

    def create_sample(self, batch: str, test: str, phase_id: str) -> str:
        sample_id = f"SMP-{batch}-{len(self.requests) + 1:03d}"
        self.requests.append({"sample_id": sample_id, "batch": batch, "test": test, "phase_id": phase_id})
        return sample_id

    def get_result(self, sample_id: str) -> float:
        return self.results[sample_id]


def zebra_label(batch: str, material: str, description: str, expiry: date, gtin: str) -> str:
    """ZPL II label for the shipper (printed on Zebra thermal printers)."""
    return (
        "^XA^CF0,30"
        f"^FO40,40^FD{description}^FS"
        f"^FO40,90^FDMaterial: {material}^FS"
        f"^FO40,130^FDBatch: {batch}^FS"
        f"^FO40,170^FDExpiry: {expiry:%Y-%m}^FS"
        f"^FO40,220^BCN,80,Y,N,N^FD(01){gtin}(10){batch}(17){expiry:%y%m%d}^FS"
        "^XZ"
    )
