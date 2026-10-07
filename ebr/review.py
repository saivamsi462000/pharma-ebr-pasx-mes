"""Review by Exception (RBE) report and the full batch record printout.

With RBE, QA reviewers focus on exceptions, out-of-limit values and manual
interventions instead of reading every page. In-limit, system-verified steps are
summarised, not listed.
"""
from ebr.engine import Batch


def review_by_exception(batch: Batch) -> str:
    completed = [r for r in batch.records if r.status == "Completed"]
    in_limit = [r for r in completed if r.value is not None and r.phase.has_limits
                and r.phase.spec["low"] <= r.value <= r.phase.spec["high"]]
    lines = [
        f"# Review by Exception — Batch {batch.batch_id}",
        "",
        f"| Field | Value |", "|---|---|",
        f"| Product | {batch.recipe.product['material']} — {batch.recipe.product['description']} |",
        f"| MBR | {batch.recipe.mbr_id} v{batch.recipe.version} |",
        f"| SAP process order | {batch.order['order_no']} |",
        f"| Batch status | **{batch.status}** |",
        f"| Phases completed | {len(completed)} / {len(batch.records)} |",
        f"| In-limit recorded parameters (no review needed) | {len(in_limit)} |",
        f"| Exceptions | {len(batch.exceptions)} "
        f"({sum(e.severity == 'Major' for e in batch.exceptions)} major) |",
        f"| Audit trail integrity | {'VERIFIED' if batch.audit.verify() else '**FAILED**'} |",
        "",
        "## Exceptions requiring QA review",
        "",
    ]
    if not batch.exceptions:
        lines.append("_No exceptions. Batch executed entirely within limits._")
    else:
        lines += ["| ID | Phase | Description | Criticality | Severity | Deviation | Status | Comment |",
                  "|---|---|---|---|---|---|---|---|"]
        for e in batch.exceptions:
            lines.append(f"| {e.exc_id} | {e.phase_id} | {e.description} | {e.criticality or '-'} | "
                         f"{e.severity} | {e.deviation_no or '-'} | {e.status} | {e.comment or '-'} |")
        lines += ["", "### Exception signatures", ""]
        for e in batch.exceptions:
            for s in e.signatures:
                lines.append(f"- {e.exc_id}: {s.manifest()}")

    lines += ["", "## Material reconciliation", "",
              "| Material | BOM (kg) | Issued (kg) | Variance % |", "|---|---|---|---|"]
    for r in batch.material_reconciliation():
        lines.append(f"| {r['material']} | {r['bom_kg']} | {r['issued_kg']} | {r['variance_pct']} |")

    hold_events = [a for a in batch.audit.entries
                   if a.action == "STATUS_CHANGE" and a.object_id == batch.batch_id
                   and "ON_HOLD" in (a.old_value or "", a.new_value or "")]
    if hold_events:
        lines += ["", "## Hold / release history", ""]
        for a in hold_events:
            lines.append(f"- {a.timestamp} · {a.user} · {a.old_value} → {a.new_value} · {a.reason or ''}")

    if batch.release_signatures:
        lines += ["", "## QA disposition", ""] + [f"- {s.manifest()}" for s in batch.release_signatures]
    return "\n".join(lines) + "\n"


def full_batch_record(batch: Batch) -> str:
    lines = [f"# Electronic Batch Record — {batch.batch_id}", ""]
    current_op = None
    for r in batch.records:
        p = r.phase
        if p.op_id != current_op:
            current_op = p.op_id
            lines += ["", f"## Operation {p.op_id} — {p.op_name}", "",
                      "| Phase | Instruction | Value | Limits | Signatures |", "|---|---|---|---|---|"]
        limits = f"{p.spec['low']} – {p.spec['high']}" if p.has_limits else "-"
        sigs = "<br>".join(s.manifest() for s in r.signatures) or "-"
        val = "-" if r.value is None else r.value
        lines.append(f"| {p.phase_id} | {p.instruction} | {val} | {limits} | {sigs} |")
    lines += ["", "## Material consumption (genealogy)", "",
              "| Material | Lot | Container | Qty (kg) |", "|---|---|---|---|"]
    for c in batch.consumption:
        lines.append(f"| {c['material']} | {c['lot']} | {c['container_id']} | {c['qty_kg']} |")
    return "\n".join(lines) + "\n"
