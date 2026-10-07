# Validation Summary Report (VSR)

| Document ID | VSR-EBR-001 |
|---|---|
| Status | Portfolio example |

## 1. Summary

The EBR simulation was validated against URS-EBR-001 using a risk-based GAMP 5 approach.

| Phase | Planned | Executed | Passed | Deviations |
|---|---|---|---|---|
| IQ | 7 steps | 7 | 7 | 0 |
| OQ (automated) | 22 test cases | 22 | 22 | 0 |
| OQ (manual) | 3 | 3 | 3 | 0 |
| PQ | PQ-01 | 1 | 1 | 0 |

## 2. Traceability

All 20 user requirements trace to functional and design elements and to at least one executed test ([RTM.md](RTM.md)).

## 3. Test incidents found during development

| # | Finding | Resolution |
|---|---|---|
| TI-01 | Demo script used an Operator as second-person verifier; RBAC correctly rejected it (Operators lack `sign_verifier`) | Demo corrected to use a Supervisor as verifier. Confirms URS-14 works as intended |

## 4. Conclusion

The system meets its intended use as defined in the URS. Every high-risk function has a technical control that an automated test has verified.
