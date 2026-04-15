CREATE TABLE IF NOT EXISTS portfolio (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    owner_name TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS program (
    id UUID PRIMARY KEY,
    portfolio_id UUID NOT NULL REFERENCES portfolio(id),
    name TEXT NOT NULL,
    sponsor_name TEXT,
    owner_name TEXT,
    current_status TEXT,
    current_phase TEXT,
    percent_complete INTEGER DEFAULT 0,
    next_milestone_name TEXT,
    next_milestone_date DATE,
    summary TEXT,
    upcoming_work TEXT,
    risk_detail TEXT,
    mitigation TEXT,
    decision_needed TEXT,
    status_note TEXT,
    next_step TEXT,
    open_risks_count INTEGER DEFAULT 0,
    escalations_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS weekly_update (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    program_id UUID NOT NULL REFERENCES program(id),
    week_ending DATE NOT NULL,
    update_status TEXT NOT NULL,
    overall_status TEXT NOT NULL,
    current_phase TEXT NOT NULL,
    percent_complete INTEGER NOT NULL,
    trend TEXT NOT NULL,
    accomplishments TEXT,
    dependencies TEXT,
    next_steps TEXT,
    executive_summary TEXT,
    submitted_at TIMESTAMPTZ,
    submitted_by TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (program_id, week_ending)
);

CREATE TABLE IF NOT EXISTS weekly_update_milestone (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    weekly_update_id UUID NOT NULL REFERENCES weekly_update(id) ON DELETE CASCADE,
    sort_order INTEGER NOT NULL,
    milestone_name TEXT,
    planned_date DATE,
    forecast_date DATE,
    status TEXT,
    comment TEXT
);

CREATE TABLE IF NOT EXISTS weekly_update_risk (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    weekly_update_id UUID NOT NULL REFERENCES weekly_update(id) ON DELETE CASCADE,
    sort_order INTEGER NOT NULL,
    severity TEXT,
    risk_title TEXT,
    owner_name TEXT,
    target_date DATE,
    description TEXT,
    mitigation TEXT
);

CREATE TABLE IF NOT EXISTS weekly_update_decision (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    weekly_update_id UUID NOT NULL REFERENCES weekly_update(id) ON DELETE CASCADE,
    sort_order INTEGER NOT NULL,
    decision_topic TEXT,
    required_by DATE,
    impact_if_unresolved TEXT,
    recommendation TEXT
);
