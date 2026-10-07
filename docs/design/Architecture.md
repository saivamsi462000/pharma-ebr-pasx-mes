# System Architecture: Pharmaceutical MES / EBR Landscape

## ISA-95 view

```mermaid
flowchart TB
    subgraph L4["Level 4: Business planning (ERP)"]
        SAP[SAP ECC<br/>PP-PI · MM · QM]
    end
    subgraph L3["Level 3: Manufacturing operations (MES)"]
        PASX[Werum PAS-X MES<br/>MBR · EBR execution · Weigh & Dispense<br/>Exceptions · Review by Exception]
        LIMS[LIMS<br/>samples & results]
        DB[(MES database<br/>SQL Server)]
    end
    subgraph L2["Level 2: Supervisory control"]
        IGN[Ignition Perspective / Vision<br/>equipment status · alarms · parameters]
    end
    subgraph L1["Level 1–0: Control & devices"]
        PLC[Allen-Bradley PLCs]
        SCALE[Scales / balances]
        SCAN[Barcode scanners]
        ZEB[Zebra printers]
    end

    SAP -- process orders, material master --> PASX
    PASX -- goods issue 261 · confirmations · GR 101 · usage decision --> SAP
    PASX <-- sample requests / results (REST/SOAP) --> LIMS
    PASX <--> DB
    IGN <-- OPC UA tags --> PLC
    PASX <-- equipment status, process values, events --> IGN
    SCALE --> PASX
    SCAN --> PASX
    PASX -- ZPL labels --> ZEB
```

## Batch data flow

```mermaid
sequenceDiagram
    participant SAP as SAP ECC
    participant MES as PAS-X / EBR
    participant OP as Operator
    participant SUP as Supervisor
    participant LIMS
    participant QA

    SAP->>MES: Process order (material, batch, qty, MBR)
    OP->>MES: Start batch
    loop Each phase
        OP->>MES: Scan equipment / containers, record values, e-sign
        SUP-->>MES: Verify (critical steps), e-sign
        MES->>SAP: Goods issue (261) per lot
    end
    MES->>LIMS: Sample request (blend uniformity)
    LIMS-->>MES: Result
    Note over MES: Out-of-limit value -> exception<br/>CQA -> batch ON HOLD
    SUP->>MES: Comment + deviation number
    QA->>MES: Close exception, lift hold
    MES->>SAP: Confirmations, goods receipt (101)
    QA->>MES: Review by Exception -> Release
    MES->>SAP: Usage decision (A)
```

## How this repository maps to PAS-X concepts

| PAS-X concept (general) | This repository |
|---|---|
| Master Batch Record (MBR) / master recipe | `recipes/MBR-TAB-500.json` |
| Process flow / operations & phases | `operations[].phases[]` |
| Building blocks for weighing, IPC, sampling, labelling | `_do_<type>` phase handlers |
| Exception handling & review by exception | `BatchException`, `review_by_exception()` |
| User roles, e-signatures | `ebr/security.py` |
| Audit trail | `ebr/audit.py` + `audit_trail` table |
| ERP interface | `SapEccGateway` |

> PAS-X is a commercial product of Körber Pharma. This repository does **not** contain PAS-X software, configuration exports or customer data. It re-implements the *concepts* in Python to demonstrate the domain knowledge and validation approach.
