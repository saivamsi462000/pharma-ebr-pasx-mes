# SOP-EBR-001: Electronic Batch Record Execution and Review by Exception

## 1. Purpose
Defines how Manufacturing executes and QA reviews batches in the EBR system.

## 2. Responsibilities

| Role | Responsibility |
|---|---|
| Operator | Executes phases, scans equipment and materials, records values, signs as performer |
| Supervisor | Second-person verification; comments exceptions and links deviations; submits batch for review |
| QA Reviewer | Closes exceptions, lifts holds, performs review by exception, releases or rejects batches |
| MES Admin | User and recipe administration only. No GMP execution or release |

## 3. Procedure

### 3.1 Batch start
1. Confirm the SAP process order has been downloaded and references the current *Approved* MBR.
2. Start the batch. The system logs `BATCH_CREATED` and `STATUS_CHANGE`.

### 3.2 Execution
1. Follow the instruction shown for the current phase. The system will not let you skip steps.
2. Scan every piece of equipment and every container. Do **not** type IDs manually.
3. If the system blocks a step (dirty equipment, expired calibration, wrong or quarantined container, weight outside tolerance), correct the cause. Never try to bypass the block.
4. Sign with your own user ID and PIN. **Never share PINs.** Three wrong PINs will lock your account.
5. For steps that need verification, a Supervisor (a different person) witnesses the action and signs.

### 3.3 Exceptions and holds
1. An out-of-limit value creates an exception automatically.
2. A **CQA** exception puts the batch **ON HOLD**. Stop and notify the Supervisor and QA.
3. The Supervisor documents the investigation in the exception comment and links the **deviation number** (mandatory for Major exceptions).
4. QA reviews and closes the exception, then lifts the hold with a documented reason.

### 3.4 Review by exception
1. After the last phase, the Supervisor submits the batch for review.
2. QA opens the **Review by Exception** report and checks that:
   - the audit-trail integrity shows **VERIFIED**
   - every exception is closed, with a deviation reference where required
   - material reconciliation variance is within limits
   - the hold/release history is justified
3. QA releases the batch, or rejects it. The system sends the usage decision to SAP.

## 4. Records
EBR, RBE report, audit trail, and e-signature report. Retain for product expiry + 1 year (minimum per site policy).

## 5. Training
All users must be trained on this SOP before they are given system access.
