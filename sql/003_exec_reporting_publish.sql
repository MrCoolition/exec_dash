CREATE INDEX IF NOT EXISTS idx_weekly_update_program_status_week
    ON weekly_update (program_id, update_status, week_ending DESC);

CREATE INDEX IF NOT EXISTS idx_weekly_update_milestone_update_sort
    ON weekly_update_milestone (weekly_update_id, sort_order);

CREATE INDEX IF NOT EXISTS idx_weekly_update_risk_update_sort
    ON weekly_update_risk (weekly_update_id, sort_order);

CREATE INDEX IF NOT EXISTS idx_weekly_update_decision_update_sort
    ON weekly_update_decision (weekly_update_id, sort_order);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'weekly_update_percent_complete_chk'
    ) THEN
        ALTER TABLE weekly_update
            ADD CONSTRAINT weekly_update_percent_complete_chk
            CHECK (percent_complete BETWEEN 0 AND 100);
    END IF;
END $$;

CREATE OR REPLACE FUNCTION publish_weekly_update(p_weekly_update_id UUID, p_submitted_by_user_id TEXT)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_update weekly_update%ROWTYPE;
    v_next_milestone_name TEXT;
    v_next_milestone_date DATE;
    v_top_risk_detail TEXT;
    v_top_risk_mitigation TEXT;
    v_open_risks_count INTEGER;
    v_escalations_count INTEGER;
    v_decision_needed TEXT;
BEGIN
    SELECT * INTO v_update
    FROM weekly_update
    WHERE id = p_weekly_update_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Weekly update % not found', p_weekly_update_id;
    END IF;

    SELECT m.milestone_name,
           COALESCE(m.forecast_date, m.planned_date)
      INTO v_next_milestone_name, v_next_milestone_date
    FROM weekly_update_milestone m
    WHERE m.weekly_update_id = p_weekly_update_id
      AND (m.forecast_date IS NOT NULL OR m.planned_date IS NOT NULL)
    ORDER BY (m.forecast_date IS NULL), COALESCE(m.forecast_date, m.planned_date), m.sort_order
    LIMIT 1;

    SELECT COALESCE(NULLIF(TRIM(r.description), ''), NULLIF(TRIM(r.risk_title), '')),
           COALESCE(NULLIF(TRIM(r.mitigation), ''), NULL)
      INTO v_top_risk_detail, v_top_risk_mitigation
    FROM weekly_update_risk r
    WHERE r.weekly_update_id = p_weekly_update_id
    ORDER BY CASE COALESCE(r.severity, '') WHEN 'High' THEN 0 WHEN 'Medium' THEN 1 WHEN 'Low' THEN 2 WHEN 'DEP' THEN 3 ELSE 4 END,
             r.sort_order,
             r.target_date NULLS LAST
    LIMIT 1;

    SELECT COUNT(*)::INTEGER,
           COUNT(*) FILTER (WHERE severity = 'High')::INTEGER
      INTO v_open_risks_count, v_escalations_count
    FROM weekly_update_risk
    WHERE weekly_update_id = p_weekly_update_id;

    SELECT NULLIF(TRIM(d.decision_topic), '')
      INTO v_decision_needed
    FROM weekly_update_decision d
    WHERE d.weekly_update_id = p_weekly_update_id
      AND NULLIF(TRIM(d.decision_topic), '') IS NOT NULL
    ORDER BY d.sort_order
    LIMIT 1;

    UPDATE program
       SET current_status = v_update.overall_status,
           current_phase = v_update.current_phase,
           percent_complete = v_update.percent_complete,
           next_milestone_name = COALESCE(v_next_milestone_name, next_milestone_name),
           next_milestone_date = COALESCE(v_next_milestone_date, next_milestone_date),
           summary = COALESCE(NULLIF(TRIM(v_update.executive_summary), ''), NULLIF(TRIM(v_update.accomplishments), ''), summary),
           upcoming_work = COALESCE(NULLIF(TRIM(v_update.next_steps), ''), upcoming_work),
           risk_detail = COALESCE(v_top_risk_detail, NULLIF(TRIM(v_update.dependencies), ''), risk_detail),
           mitigation = COALESCE(v_top_risk_mitigation, mitigation),
           decision_needed = v_decision_needed,
           status_note = COALESCE(NULLIF(TRIM(v_update.executive_summary), ''), NULLIF(TRIM(v_update.dependencies), ''), status_note),
           next_step = COALESCE(NULLIF(TRIM(v_update.next_steps), ''), next_step),
           open_risks_count = COALESCE(v_open_risks_count, 0),
           escalations_count = COALESCE(v_escalations_count, 0)
     WHERE id = v_update.program_id;
END;
$$;
