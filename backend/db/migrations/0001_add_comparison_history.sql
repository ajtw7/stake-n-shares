-- Postgres: ensure uuid extension if you want UUIDs
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE comparison_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  payload JSONB NOT NULL,
  result JSONB NOT NULL,
  params JSONB,
  notes TEXT
);