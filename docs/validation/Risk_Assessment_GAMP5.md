# Risk Assessment (GAMP 5 / FMEA)

| Document ID | RA-EBR-001 |
|---|---|

Scoring: Severity (S) × Probability (P) × Detectability (D), each 1–3. RPN ≥ 12 is **High** and needs a dedicated test plus a procedural control.

| # | Function | Failure mode | Impact on patient / product / data | S | P | D | RPN | Control | Verified by |
|---|---|---|---|---|---|---|---|---|---|
| R1 | Dispensing | Wrong material weighed | Wrong composition → patient safety | 3 | 2 | 3 | **18** | Barcode identity check; status and expiry check | URS-05 tests |
| R2 | Dispensing | Weight out of tolerance | Potency out of spec | 3 | 2 | 2 | **12** | Tolerance check; forced re-weigh | URS-06 test |
| R3 | Execution | Step skipped | Unverified process | 3 | 1 | 3 | 9 | Sequence enforcement | URS-03 test |
| R4 | IPC | CQA excursion not noticed | Defective product released | 3 | 2 | 2 | **12** | Automatic exception + hold | URS-07/08 tests |
| R5 | Release | Release with open issues | Non-conforming product released | 3 | 1 | 3 | 9 | Release blocked while exceptions are open | URS-10 test |
| R6 | E-signature | Signature by an unauthorised person | Data integrity (attributable) | 3 | 2 | 3 | **18** | RBAC, re-authentication, lockout | URS-13/14 tests |
| R7 | Audit trail | Record altered without trace | Data integrity (ALCOA+) | 3 | 1 | 3 | 9 | Hash chain + DB triggers | URS-15/16 tests |
| R8 | SAP interface | Goods issue lost | Inventory mismatch; genealogy gap | 2 | 2 | 2 | 8 | Outbox + reconciliation | URS-11 test, OQ-20 |
| R9 | Equipment | Dirty / uncalibrated equipment used | Contamination, wrong measurements | 3 | 2 | 2 | **12** | Status check before use | URS-04 tests |
| R10 | Labelling | Wrong batch or expiry on label | Mislabelled product | 3 | 1 | 2 | 6 | Label data pulled from batch record; verifier sign | OQ-19 |

**Conclusion:** All high-risk items (R1, R2, R4, R6, R9) have a technical control **and** an automated test. Medium and low items are covered by a test or a procedural control (see the SOP).
