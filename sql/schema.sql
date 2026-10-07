-- EBR persistence model (ANSI SQL; tested on SQLite, written to port to SQL Server)

CREATE TABLE batch (
    batch_id        VARCHAR(20) PRIMARY KEY,
    order_no        VARCHAR(20) NOT NULL,
    material        VARCHAR(20) NOT NULL,
    mbr_id          VARCHAR(20) NOT NULL,
    mbr_version     VARCHAR(10) NOT NULL,
    status          VARCHAR(20) NOT NULL
);

CREATE TABLE phase_record (
    batch_id        VARCHAR(20) NOT NULL REFERENCES batch(batch_id),
    phase_id        VARCHAR(10) NOT NULL,
    op_name         VARCHAR(50) NOT NULL,
    phase_type      VARCHAR(30) NOT NULL,
    parameter       VARCHAR(50),
    value           DECIMAL(12,3),
    low_limit       DECIMAL(12,3),
    high_limit      DECIMAL(12,3),
    criticality     VARCHAR(5),
    completed_at    VARCHAR(30),
    PRIMARY KEY (batch_id, phase_id)
);

CREATE TABLE e_signature (
    sig_id          INTEGER PRIMARY KEY,
    record_id       VARCHAR(30) NOT NULL,
    batch_id        VARCHAR(20) NOT NULL REFERENCES batch(batch_id),
    user_id         VARCHAR(30) NOT NULL,
    printed_name    VARCHAR(80) NOT NULL,
    meaning         VARCHAR(40) NOT NULL,
    signed_at       VARCHAR(30) NOT NULL
);

CREATE TABLE batch_exception (
    exc_id          VARCHAR(30) PRIMARY KEY,
    batch_id        VARCHAR(20) NOT NULL REFERENCES batch(batch_id),
    phase_id        VARCHAR(10) NOT NULL,
    description     VARCHAR(200) NOT NULL,
    criticality     VARCHAR(5),
    severity        VARCHAR(10) NOT NULL,
    deviation_no    VARCHAR(20),
    status          VARCHAR(10) NOT NULL CHECK (status IN ('Open', 'Commented', 'Closed'))
);

CREATE TABLE material_consumption (
    batch_id        VARCHAR(20) NOT NULL REFERENCES batch(batch_id),
    material        VARCHAR(20) NOT NULL,
    lot             VARCHAR(20) NOT NULL,
    container_id    VARCHAR(20) NOT NULL,
    qty_kg          DECIMAL(10,3) NOT NULL CHECK (qty_kg > 0)
);

CREATE TABLE audit_trail (
    seq             INTEGER PRIMARY KEY,
    ts_utc          VARCHAR(30) NOT NULL,
    user_id         VARCHAR(30) NOT NULL,
    action          VARCHAR(30) NOT NULL,
    object_id       VARCHAR(40) NOT NULL,
    old_value       VARCHAR(200),
    new_value       VARCHAR(200),
    reason          VARCHAR(200),
    prev_hash       CHAR(64) NOT NULL,
    hash            CHAR(64) NOT NULL UNIQUE
);

-- Part 11: the audit trail is append-only. Updates and deletes are rejected at the database level.
CREATE TRIGGER audit_no_update BEFORE UPDATE ON audit_trail
BEGIN SELECT RAISE(ABORT, 'audit_trail is append-only'); END;
CREATE TRIGGER audit_no_delete BEFORE DELETE ON audit_trail
BEGIN SELECT RAISE(ABORT, 'audit_trail is append-only'); END;
