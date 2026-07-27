-- PostgreSQL initialization script
-- Runs once when the container is first created

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for future full-text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create read-only role for analytics (future use)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'pds_readonly') THEN
        CREATE ROLE pds_readonly;
    END IF;
END
$$;

GRANT CONNECT ON DATABASE pds_sentinel TO pds_readonly;
