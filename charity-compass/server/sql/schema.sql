-- Database schema for Charity Compass service.

CREATE TABLE IF NOT EXISTS charities (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    mission TEXT,
    website TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
