# Change Request: CR-EBR-2026-014 (worked example)

| Field | Entry |
|---|---|
| Title | Tighten tablet-weight IPC limits on MBR-TAB-500 |
| Requested by | Process Engineering |
| System | EBR / MBR-TAB-500 |
| Change type | Configuration (master recipe) |
| GxP impact | Yes |

## 1. Description

Change phase `0040-01` (average tablet weight) limits from **585–615 mg** to **588–612 mg** (±2%) following the process capability review.

## 2. Impact assessment

| Area | Impact | Action |
|---|---|---|
| MBR | New version v3.1 | Author → QA approve |
| Batches in progress | None. Running batches keep v3.0 | Confirm no open batch is on v3.0 at cut-over |
| Validation | Regression on URS-07 / URS-08 | Re-run OQ-07, OQ-08; run boundary values 587.9 / 588.0 / 612.0 / 612.1 |
| SAP | None | — |
| Training | Operators made aware of the new limits | Read-and-understand |
| SOP | None | — |

## 3. Implementation plan

1. **DEV:** edit `recipes/MBR-TAB-500.json`, bump the version to 3.1, run `pytest`.
2. **QA environment:** execute the regression tests plus boundary tests; attach the evidence.
3. **QA approval** of MBR v3.1 (status → Approved).
4. **PROD deployment** in a planned window; record the Git commit hash and MBR checksum (IQ-02, IQ-06).
5. Post-implementation verification: first batch on v3.1 reviewed by QA.

## 4. Approvals

| Role | Name | E-signature / date |
|---|---|---|
| Change owner | | |
| System owner | | |
| QA | | |

## 5. Closure

| Check | Result |
|---|---|
| Tests executed and passed | |
| Documents updated (RTM, MBR) | |
| Effectiveness check | |
