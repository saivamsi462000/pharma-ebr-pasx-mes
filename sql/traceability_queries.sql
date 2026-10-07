-- name: backward_genealogy
-- Which raw-material lots went into a finished batch? (recall / complaint investigation)
SELECT b.batch_id, b.material AS finished_material, mc.material AS component,
       mc.lot, mc.container_id, mc.qty_kg
FROM batch b
JOIN material_consumption mc ON mc.batch_id = b.batch_id
WHERE b.batch_id = :batch_id
ORDER BY mc.material;

-- name: forward_genealogy
-- Which finished batches used a given raw-material lot? (supplier quality issue)
SELECT mc.lot, b.batch_id, b.material, b.status
FROM material_consumption mc
JOIN batch b ON b.batch_id = mc.batch_id
WHERE mc.lot = :lot;

-- name: exception_report
SELECT e.batch_id, e.exc_id, e.phase_id, e.description, e.criticality,
       e.severity, e.deviation_no, e.status
FROM batch_exception e
ORDER BY e.batch_id, e.exc_id;

-- name: cpp_cqa_summary
-- Recorded critical parameters with distance from target range (process capability input)
SELECT batch_id, phase_id, parameter, value, low_limit, high_limit, criticality,
       CASE WHEN value < low_limit OR value > high_limit THEN 'OUT' ELSE 'IN' END AS in_spec
FROM phase_record
WHERE criticality IN ('CPP', 'CQA')
ORDER BY batch_id, phase_id;

-- name: signature_report
-- User access / e-signature report for audit readiness
SELECT user_id, printed_name, meaning, COUNT(*) AS signatures,
       MIN(signed_at) AS first_signed, MAX(signed_at) AS last_signed
FROM e_signature
GROUP BY user_id, printed_name, meaning
ORDER BY user_id;
