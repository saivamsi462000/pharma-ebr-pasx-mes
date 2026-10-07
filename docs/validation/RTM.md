# Requirements Traceability Matrix (RTM)

| Document ID | RTM-EBR-001 |
|---|---|

Every URS requirement traces to a functional spec item, a design element and at least one test. Automated OQ tests live in `tests/test_ebr.py`. Run them with `pytest -v`.

| URS | FS | Design element | Test case(s) | Risk | Result |
|---|---|---|---|---|---|
| URS-01 | FS-01 | `MasterRecipe.require_approved` | `test_URS_01_only_approved_mbr_can_create_batch` | High | Pass |
| URS-02 | FS-02 | `MasterRecipe.validate` | `test_URS_02_mbr_validation_rejects_bad_limits` | Medium | Pass |
| URS-03 | FS-03 | `Batch.next_phase`, sequence check | `test_URS_03_phases_cannot_be_skipped` | High | Pass |
| URS-04 | FS-04 | `_do_equipment_check` | `test_URS_04_dirty_equipment_blocks_execution`, `test_URS_04_expired_calibration_blocks_execution` | High | Pass |
| URS-05 | FS-05 | `_do_weigh_dispense` scan checks | `test_URS_05_wrong_material_scan_rejected`, `test_URS_05_quarantined_container_rejected` | High | Pass |
| URS-06 | FS-05 | tolerance check | `test_URS_06_weight_outside_tolerance_rejected` | High | Pass |
| URS-07 | FS-06 | `_raise_exception` | `test_URS_07_out_of_limit_value_creates_exception` | High | Pass |
| URS-08 | FS-07 | CQA → `ON_HOLD` | `test_URS_08_cqa_excursion_puts_batch_on_hold` | High | Pass |
| URS-09 | FS-08 | `qa_close_exception` | `test_URS_09_major_exception_requires_deviation` | High | Pass |
| URS-10 | FS-09 | `qa_disposition` | `test_URS_10_release_blocked_with_open_exception` | High | Pass |
| URS-11 | FS-10 | `SapEccGateway` | `test_URS_11_happy_path_release_and_sap_messages` | High | Pass |
| URS-12 | FS-11 | dual-signature logic | `test_URS_12_performer_and_verifier_must_differ`, `test_URS_12_verification_required` | High | Pass |
| URS-13 | FS-12 | `UserDirectory.sign`, lockout | `test_URS_13_wrong_pin_rejected_and_account_locked` | High | Pass |
| URS-14 | FS-13 | `PERMISSIONS` | `test_URS_14_operator_cannot_release_batch`, `test_URS_14_admin_has_no_gmp_execution_rights` | High | Pass |
| URS-15 | FS-14 | `AuditTrail.verify`, `ESignature.manifest` | `test_URS_15_audit_trail_detects_tampering`, `test_URS_15_signature_manifest_contents` | High | Pass |
| URS-16 | FS-15 | SQL triggers | `test_URS_16_database_audit_trail_is_append_only` | High | Pass |
| URS-17 | FS-16 | genealogy queries | `test_URS_17_backward_and_forward_genealogy` | High | Pass |
| URS-18 | FS-17 | `review_by_exception` | OQ-18 (manual review of `output/review_by_exception.md`) | Low | Pass |
| URS-19 | FS-18 | `zebra_label` | OQ-19 (manual check of `output/shipper_label.zpl` in a ZPL viewer) | Medium | Pass |
| URS-20 | FS-19 | `material_reconciliation` | OQ-20 (manual check of reconciliation table vs dispensed weights) | Medium | Pass |

**Coverage:** 20 of 20 requirements traced; 17 verified by automated tests (22 test cases) and 3 by documented manual tests.
