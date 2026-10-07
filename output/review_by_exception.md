# Review by Exception — Batch B260302

| Field | Value |
|---|---|
| Product | FG-100500 — Generic Film-Coated Tablet 500 mg (training product) |
| MBR | MBR-TAB-500 v3.0 |
| SAP process order | PO-1000452 |
| Batch status | **RELEASED** |
| Phases completed | 17 / 17 |
| In-limit recorded parameters (no review needed) | 9 |
| Exceptions | 2 (2 major) |
| Audit trail integrity | VERIFIED |

## Exceptions requiring QA review

| ID | Phase | Description | Criticality | Severity | Deviation | Status | Comment |
|---|---|---|---|---|---|---|---|
| EXC-B260302-01 | 0040-02 | hardness_kp = 9.4 outside [10, 18] | CQA | Major | DEV-2026-0117 | Closed | Press tooling wear found; punches replaced, 20-tablet re-test mean 13.8 kp |
| EXC-B260302-02 | 0050-01 | exhaust_temp_c = 46.8 outside [38, 46] | CPP | Major | DEV-2026-0118 | Closed | Transient 0.8 °C excursion for 2 min during spray-rate ramp; within PAR per validation report |

### Exception signatures

- EXC-B260302-01: R. Patel (sup.rpatel) | Exception commented | 2026-10-07T22:25:32+00:00
- EXC-B260302-01: K. Chen (qa.kchen) | Approved by QA | 2026-10-07T22:25:32+00:00
- EXC-B260302-02: R. Patel (sup.rpatel) | Exception commented | 2026-10-07T22:25:32+00:00
- EXC-B260302-02: K. Chen (qa.kchen) | Approved by QA | 2026-10-07T22:25:32+00:00

## Material reconciliation

| Material | BOM (kg) | Issued (kg) | Variance % |
|---|---|---|---|
| RM-API-500 | 100.0 | 100.12 | 0.12 |
| RM-MCC-101 | 14.4 | 14.38 | -0.139 |
| RM-PVP-K30 | 3.6 | 3.61 | 0.278 |
| RM-MGST-01 | 1.2 | 1.21 | 0.833 |
| RM-COAT-WH | 0.8 | 0.8 | 0.0 |

## Hold / release history

- 2026-10-07T22:25:32+00:00 · system · IN_EXECUTION → ON_HOLD · CQA excursion EXC-B260302-01
- 2026-10-07T22:25:32+00:00 · qa.kchen · ON_HOLD → IN_EXECUTION · DEV-2026-0117 assessed; product impact none after tooling change

## QA disposition

- K. Chen (qa.kchen) | Released by QA | 2026-10-07T22:25:32+00:00
