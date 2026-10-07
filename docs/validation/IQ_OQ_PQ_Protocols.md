# Qualification Protocols: IQ / OQ / PQ

| Document ID | QP-EBR-001 |
|---|---|

---

## Installation Qualification (IQ)

**Objective:** Verify that the software is installed in the target environment as specified.

| Step | Instruction | Acceptance criterion | Result | Initials / date |
|---|---|---|---|---|
| IQ-01 | Record the OS and Python version (`python --version`) | Python ≥ 3.10 | | |
| IQ-02 | Record the Git commit hash of the release (`git rev-parse HEAD`) | Matches the release in the change record | | |
| IQ-03 | Install dependencies (`pip install -r requirements.txt`) | Completes without errors | | |
| IQ-04 | Verify that the files listed in DS §1 exist | All present | | |
| IQ-05 | Create the database from `sql/schema.sql` | 6 tables and 2 triggers created | | |
| IQ-06 | Verify the MBR file checksum (`shasum -a 256 recipes/MBR-TAB-500.json`) | Matches the approved MBR checksum | | |
| IQ-07 | Verify that the system clock is synchronised (NTP) | Offset < 1 s | | |

---

## Operational Qualification (OQ)

**Objective:** Verify that each function works as specified across normal, boundary and error conditions.

**Automated execution:** run `pytest -v` and attach the output as evidence. The test-to-requirement mapping is in [RTM.md](RTM.md).

| Test ID | Requirement | Scenario | Expected result |
|---|---|---|---|
| OQ-01 | URS-01 | Create a batch with a Draft MBR | Rejected with RecipeError |
| OQ-03 | URS-03 | Execute phase 0020-02 before 0010-01 | "Out of sequence" error |
| OQ-04a/b | URS-04 | Dirty balance / calibration expired | Execution blocked |
| OQ-05a/b | URS-05 | Scan the API container for MCC / scan a quarantined container | Blocked |
| OQ-06 | URS-06 | Dispense 101.0 kg API (target 100 ± 0.5) | Re-weigh required |
| OQ-07 | URS-07 | Record impeller speed 171 rpm (limit 140–160) | Major exception created |
| OQ-08 | URS-08 | Record hardness 8.0 kp (CQA 10–18) | Batch ON_HOLD; next phase blocked |
| OQ-09 | URS-09 | Close a major exception without a deviation number | Rejected |
| OQ-10 | URS-10 | Release with an open exception | Rejected |
| OQ-11 | URS-11 | Complete a clean batch and release it | 5× GI, 6× confirmation, 1× GR, 1× usage decision |
| OQ-12a/b | URS-12 | Same user as performer and verifier / missing verifier | Rejected |
| OQ-13 | URS-13 | 3 wrong PINs | Account locked; ACCOUNT_LOCKED audit entry |
| OQ-14a/b | URS-14 | Operator attempts release / admin permissions | AccessDenied / no GMP rights |
| OQ-15a/b | URS-15 | Modify one audit entry / inspect the signature manifest | `verify()` = False / name, meaning and time shown |
| OQ-16 | URS-16 | SQL UPDATE / DELETE on audit_trail | Aborted "append-only" |
| OQ-17 | URS-17 | Backward genealogy for B260302; forward for lot L-API-2601 | 5 components; batch found |
| OQ-18 | URS-18 | Review the RBE report | Shows only exceptions, holds, reconciliation; integrity VERIFIED |
| OQ-19 | URS-19 | Render the ZPL label | Batch, expiry and GS1 barcode correct |
| OQ-20 | URS-20 | Compare reconciliation with dispensed weights | Values match; variance % correct |

---

## Performance Qualification (PQ)

**Objective:** Show that the system supports the real business process, end to end, with trained users and representative data.

| Step | Scenario | Acceptance criterion |
|---|---|---|
| PQ-01 | Run `python run_demo.py`: full batch B260302 from SAP order to QA release, including one CQA hold and one CPP excursion | Final status RELEASED; both exceptions closed with deviation numbers |
| PQ-02 | QA reviewer performs review by exception using `output/review_by_exception.md` only | Reviewer can disposition the batch without opening the full EBR; review time recorded |
| PQ-03 | Reconcile SAP outbox (`output/sap_outbox.json`) with batch consumption | 100% of dispensed lots have a matching GI; GR quantity = good units |
| PQ-04 | Audit-readiness drill: produce the e-signature report and audit trail for B260302 | Delivered within 15 minutes; chain verified |
| PQ-05 | Execute three consecutive batches | All three meet PQ-01 … PQ-03 |

**Evidence from the portfolio run:** PQ-01 passed. Final status RELEASED, yield 97.61%, 13 SAP messages, 70 audit entries, chain verified.
