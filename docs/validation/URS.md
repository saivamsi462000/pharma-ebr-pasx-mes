# User Requirements Specification (URS)

| Document ID | URS-EBR-001 |
|---|---|
| System | Electronic Batch Record (EBR) execution — solid oral dose (training product) |
| GAMP 5 category | Category 4 (configured product) for the MES; Category 5 for custom interface logic |
| Version | 1.0 |
| Status | Portfolio example — not an executed GMP document |

## 1. Purpose

This document defines what the users need from an MES-based Electronic Batch Record. The system replaces paper batch records for a film-coated tablet process (dispensing → granulation → blending → compression → coating → packaging) and must meet GMP, FDA 21 CFR Part 11 and EU GMP Annex 11.

## 2. Scope

**In scope:** master batch record (MBR) management, batch execution, weighing and dispensing, in-process controls, exception handling, electronic signatures, audit trail, review by exception, and interfaces to SAP ECC, LIMS and label printers.
**Out of scope:** scheduling, warehouse management, equipment automation logic (PLC).

## 3. Requirements

Priority: **M** = mandatory (GxP), **D** = desirable.

| ID | Requirement | Priority | GxP |
|---|---|---|---|
| URS-01 | Only MBRs in *Approved* status can be used to create batches. | M | Yes |
| URS-02 | The system shall validate MBR content (unique steps, valid limits, BOM consistency) before approval. | M | Yes |
| URS-03 | Steps shall execute in the sequence defined by the MBR. Skipping steps shall not be possible. | M | Yes |
| URS-04 | Equipment shall be verified as *Clean* and within calibration before use. | M | Yes |
| URS-05 | Materials shall be identified by barcode scan. Wrong, quarantined, rejected or expired containers shall be blocked. | M | Yes |
| URS-06 | Dispensed quantities shall be within the BOM tolerance; otherwise re-weigh is enforced. | M | Yes |
| URS-07 | Values outside defined limits shall automatically create a documented exception classified by criticality (CPP/CQA/KPI). | M | Yes |
| URS-08 | A CQA excursion shall place the batch on *Hold*, blocking further execution until QA lifts the hold with an e-signature. | M | Yes |
| URS-09 | Major exceptions shall reference a deviation number before QA closure. | M | Yes |
| URS-10 | A batch cannot be released while any exception remains open. | M | Yes |
| URS-11 | The system shall exchange data with SAP ECC: receive process orders; send goods issues (261), confirmations, goods receipts (101) and usage decisions. | M | Yes |
| URS-12 | Critical steps shall require a second-person verification by a different individual. | M | Yes |
| URS-13 | E-signatures shall require re-authentication. Three failed attempts shall lock the account. | M | Yes |
| URS-14 | Access shall be role-based. Administrators shall have no GMP execution or release rights (segregation of duties). | M | Yes |
| URS-15 | A secure, computer-generated, time-stamped audit trail shall record all GMP actions and detect tampering. Signature manifests shall show name, date/time and meaning. | M | Yes |
| URS-16 | Audit-trail records shall not be modifiable or deletable, including at the database level. | M | Yes |
| URS-17 | The system shall provide backward and forward material genealogy. | M | Yes |
| URS-18 | The system shall provide a Review-by-Exception report listing only exceptions, holds and reconciliation results. | D | Yes |
| URS-19 | Shipper labels shall be printed from batch data (batch, expiry, GTIN) on Zebra printers. | M | Yes |
| URS-20 | Material reconciliation (BOM vs issued) shall be calculated automatically. | M | Yes |

## 4. Regulatory references

- 21 CFR Part 11: Electronic Records; Electronic Signatures
- 21 CFR Part 211: cGMP for Finished Pharmaceuticals (§211.186 master records, §211.188 batch records, §211.192 review)
- EU GMP Annex 11: Computerised Systems
- ISPE GAMP 5 (2nd ed.): A Risk-Based Approach to Compliant GxP Computerized Systems
- ISA-95: Enterprise–Control System Integration
