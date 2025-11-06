-- Fix database permissions for euro_camp_db
-- Run this as the PostgreSQL superuser (postgres)
-- Usage: psql -U postgres -d euro_camp_db -f fix_db_permissions.sql

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE euro_camp_db TO "user";

-- Grant privileges on all tables in the public schema
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "user";

-- Grant privileges on all sequences in the public schema
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "user";

-- Transfer ownership of all tables to the user
ALTER TABLE IF EXISTS core_campsite OWNER TO "user";
ALTER TABLE IF EXISTS accounts_user OWNER TO "user";
ALTER TABLE IF EXISTS accounts_user_groups OWNER TO "user";
ALTER TABLE IF EXISTS accounts_user_user_permissions OWNER TO "user";

-- Grant default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO "user";
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO "user";

-- Verify permissions (optional)
\dt
