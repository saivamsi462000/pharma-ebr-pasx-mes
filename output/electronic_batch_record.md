# Electronic Batch Record — B260302


## Operation 0010 — Dispensing

| Phase | Instruction | Value | Limits | Signatures |
|---|---|---|---|---|
| 0010-01 | Verify dispensing booth line clearance and cleaning status label | - | - | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00<br>R. Patel (sup.rpatel) | Verified by | 2026-10-07T22:25:32+00:00 |
| 0010-02 | Scan booth and balance; confirm calibration status is valid | - | - | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00 |
| 0010-03 | Weigh and dispense each BOM material against scanned container | - | - | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00<br>R. Patel (sup.rpatel) | Verified by | 2026-10-07T22:25:32+00:00 |

## Operation 0020 — Wet Granulation

| Phase | Instruction | Value | Limits | Signatures |
|---|---|---|---|---|
| 0020-01 | Scan granulator; confirm clean and calibrated | - | - | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00 |
| 0020-02 | Record impeller speed during wet massing | 152 | 140 – 160 | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00 |
| 0020-03 | Record granulation end-point power consumption | 12.4 | 11.0 – 13.0 | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00 |
| 0020-04 | Record LOD after fluid-bed drying | 1.8 | 1.0 – 3.0 | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00<br>R. Patel (sup.rpatel) | Verified by | 2026-10-07T22:25:32+00:00 |

## Operation 0030 — Blending

| Phase | Instruction | Value | Limits | Signatures |
|---|---|---|---|---|
| 0030-01 | Record blend time | 15 | 14 – 16 | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00 |
| 0030-02 | Pull 10 blend-uniformity samples; send to QC (LIMS) | - | - | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00<br>R. Patel (sup.rpatel) | Verified by | 2026-10-07T22:25:32+00:00 |
| 0030-03 | Retrieve blend uniformity RSD from LIMS | 2.8 | 0.0 – 5.0 | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00 |

## Operation 0040 — Compression

| Phase | Instruction | Value | Limits | Signatures |
|---|---|---|---|---|
| 0040-01 | Record average tablet weight (IPC) | 601.5 | 585 – 615 | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00 |
| 0040-02 | Record tablet hardness (IPC) | 9.4 | 10 – 18 | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00 |
| 0040-03 | Record main compression force | 18.6 | 15 – 21 | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00 |

## Operation 0050 — Film Coating

| Phase | Instruction | Value | Limits | Signatures |
|---|---|---|---|---|
| 0050-01 | Record exhaust air temperature | 46.8 | 38 – 46 | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00 |
| 0050-02 | Record coating weight gain | 3.1 | 2.5 – 3.5 | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00<br>R. Patel (sup.rpatel) | Verified by | 2026-10-07T22:25:32+00:00 |

## Operation 0060 — Packaging

| Phase | Instruction | Value | Limits | Signatures |
|---|---|---|---|---|
| 0060-01 | Print and verify shipper labels (Zebra) with batch, expiry and GTIN | - | - | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00<br>R. Patel (sup.rpatel) | Verified by | 2026-10-07T22:25:32+00:00 |
| 0060-02 | Record good tablets packed; system calculates yield | 97.61 | 95.0 – 101.0 | J. Smith (op.jsmith) | Performed by | 2026-10-07T22:25:32+00:00<br>R. Patel (sup.rpatel) | Verified by | 2026-10-07T22:25:32+00:00 |

## Material consumption (genealogy)

| Material | Lot | Container | Qty (kg) |
|---|---|---|---|
| RM-API-500 | L-API-2601 | C-0001 | 100.12 |
| RM-MCC-101 | L-MCC-2588 | C-0002 | 14.38 |
| RM-PVP-K30 | L-PVP-2542 | C-0003 | 3.61 |
| RM-MGST-01 | L-MGS-2519 | C-0004 | 1.21 |
| RM-COAT-WH | L-CWH-2607 | C-0005 | 0.8 |
