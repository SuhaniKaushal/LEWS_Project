-- ============================================================================
-- Multi-Tenant Migration Script for Net.py Sensor Data System
-- ============================================================================
-- Purpose: Add tenant_id support to enable multi-tenant architecture
-- Date: 2026-01-07
-- Database: netala_database (PostgreSQL)
-- Python Version: 3.9.13
--
-- IMPORTANT: Backup your database before running this script!
-- Command: pg_dump -U postgres -d netala_database > backup_$(date +%Y%m%d).sql
-- ============================================================================

-- Step 1: Create the tenant table
-- ============================================================================
CREATE TABLE IF NOT EXISTS tenant (
    tenant_id SERIAL PRIMARY KEY,
    tenant_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    contact_email VARCHAR(100) DEFAULT NULL,
    settings JSONB,
    remarks TEXT
);

COMMENT ON TABLE tenant IS 'Stores tenant/organization information for multi-tenant isolation';
COMMENT ON COLUMN tenant.tenant_id IS 'Auto-incrementing unique identifier for tenant';
COMMENT ON COLUMN tenant.tenant_name IS 'Display name of the tenant/organization';
COMMENT ON COLUMN tenant.is_active IS 'Whether tenant is active (true) or suspended (false)';
COMMENT ON COLUMN tenant.settings IS 'JSON configuration settings for tenant';

-- Step 2: Add tenant_id column to node table
-- ============================================================================
ALTER TABLE node ADD COLUMN IF NOT EXISTS tenant_id INTEGER;

COMMENT ON COLUMN node.tenant_id IS 'Foreign key to tenant table for multi-tenant isolation';

-- Step 3: Add tenant_id column to sensor_info table
-- ============================================================================
ALTER TABLE sensor_info ADD COLUMN IF NOT EXISTS tenant_id INTEGER;

COMMENT ON COLUMN sensor_info.tenant_id IS 'Foreign key to tenant table for multi-tenant isolation';

-- Step 4: Add tenant_id column to sensor_data table (CRITICAL for performance)
-- ============================================================================
ALTER TABLE sensor_data ADD COLUMN IF NOT EXISTS tenant_id INTEGER;

COMMENT ON COLUMN sensor_data.tenant_id IS 'Foreign key to tenant table - indexed for query performance';

-- Step 5: Add tenant_id column to sensor_thresold table
-- ============================================================================
ALTER TABLE sensor_thresold ADD COLUMN IF NOT EXISTS tenant_id INTEGER;

COMMENT ON COLUMN sensor_thresold.tenant_id IS 'Foreign key to tenant table for tenant-specific thresholds';

-- Step 6: Add tenant_id column to user_list table
-- ============================================================================
ALTER TABLE user_list ADD COLUMN IF NOT EXISTS tenant_id INTEGER;

COMMENT ON COLUMN user_list.tenant_id IS 'Foreign key to tenant table - assigns users to tenants';

-- Step 7: Add tenant_id column to sensor_list table
-- ============================================================================
-- Option A: Per-tenant sensor types (uncomment if you want tenant-specific sensor types)
ALTER TABLE sensor_list ADD COLUMN IF NOT EXISTS tenant_id INTEGER;

COMMENT ON COLUMN sensor_list.tenant_id IS 'Foreign key to tenant table - tenant-specific sensor types';

-- Step 8: Add tenant_id column to u_status table (if exists)
-- ============================================================================
-- Check if u_status table exists before adding column
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'u_status') THEN
        ALTER TABLE u_status ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
    END IF;
END $$;

-- Step 9: Create default tenant for existing data
-- ============================================================================
INSERT INTO tenant (tenant_name, contact_email, is_active, remarks)
VALUES ('Default Organization', 'admin@example.com', TRUE, 'Default tenant for migrated existing data')
ON CONFLICT DO NOTHING
RETURNING tenant_id;

-- Note: tenant_id will be auto-generated (starts at 1)

-- Step 10: Migrate existing data to default tenant
-- ============================================================================
-- Assign all existing NULL tenant_id records to tenant_id = 1 (default tenant)

UPDATE node
SET tenant_id = 1
WHERE tenant_id IS NULL;

UPDATE sensor_info
SET tenant_id = 1
WHERE tenant_id IS NULL;

UPDATE sensor_data
SET tenant_id = 1
WHERE tenant_id IS NULL;

UPDATE sensor_thresold
SET tenant_id = 1
WHERE tenant_id IS NULL;

UPDATE user_list
SET tenant_id = 1
WHERE tenant_id IS NULL;

UPDATE sensor_list
SET tenant_id = 1
WHERE tenant_id IS NULL;

-- Update u_status if it exists
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'u_status') THEN
        UPDATE u_status SET tenant_id = 1 WHERE tenant_id IS NULL;
    END IF;
END $$;

-- Step 11: Add composite unique constraints for multi-tenant data isolation
-- ============================================================================
-- These constraints ensure uniqueness within each tenant's scope

-- user_list: (tenant_id, email_id) composite unique
ALTER TABLE user_list
DROP CONSTRAINT IF EXISTS email_id_primary_key CASCADE,
ADD CONSTRAINT email_id_primary_key PRIMARY KEY (tenant_id, email_id);

COMMENT ON CONSTRAINT email_id_primary_key ON user_list IS 'Composite PK: email_id unique per tenant';

-- node: Keep existing node_id as PK (already globally unique)
-- Add unique constraint for tenant scope
ALTER TABLE node
DROP CONSTRAINT IF EXISTS node_pkey CASCADE,
ADD CONSTRAINT uq_node_tenant_nodeid UNIQUE (tenant_id, node_id);

COMMENT ON CONSTRAINT uq_node_tenant_nodeid ON node IS 'Ensures node_id is unique within tenant scope';

-- sensor_info: (tenant_id, sensor_id) composite unique
ALTER TABLE sensor_info
DROP CONSTRAINT IF EXISTS sensor_info_pkey CASCADE,
ADD CONSTRAINT sensor_info_pkey PRIMARY KEY (tenant_id, sensor_id);

COMMENT ON CONSTRAINT sensor_info_pkey ON sensor_info IS 'Composite PK: sensor_id unique per tenant';

-- sensor_data: (tenant_id, sensor_id, receive_time) composite unique
-- Note: sensor_data already has unique constraint on (sensor_id, receive_time)
-- We need to update it to include tenant_id
ALTER TABLE sensor_data
DROP CONSTRAINT IF EXISTS sensor_data_pkey CASCADE,
ADD CONSTRAINT uq_sensor_data_tenant_sensor_time UNIQUE (tenant_id, sensor_id, receive_time);

COMMENT ON CONSTRAINT uq_sensor_data_tenant_sensor_time ON sensor_data IS 'Composite unique: one reading per sensor per timestamp per tenant';

-- sensor_thresold: (tenant_id, sensor_id) composite unique
ALTER TABLE sensor_thresold
DROP CONSTRAINT IF EXISTS sensor_thresold_pkey CASCADE,
ADD CONSTRAINT sensor_thresold_pkey PRIMARY KEY (tenant_id, sensor_id);

COMMENT ON CONSTRAINT sensor_thresold_pkey ON sensor_thresold IS 'Composite PK: one threshold config per sensor per tenant';

-- u_status: (tenant_id, email_id, location) composite unique (if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'u_status') THEN
        ALTER TABLE u_status
        DROP CONSTRAINT IF EXISTS u_status_pkey CASCADE,
        ADD CONSTRAINT uq_u_status_tenant_email_location UNIQUE (tenant_id, email_id, location);
    END IF;
END $$;

-- Step 12: Create indexes for performance
-- ============================================================================
-- Index on node.tenant_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_node_tenant_id ON node(tenant_id);

-- Index on sensor_info.tenant_id for faster lookups (covered by PK, but explicit)
CREATE INDEX IF NOT EXISTS idx_sensor_info_tenant_id ON sensor_info(tenant_id);

-- Composite index on sensor_data for time-series queries (CRITICAL for performance)
CREATE INDEX IF NOT EXISTS idx_sensor_data_tenant_time ON sensor_data(tenant_id, receive_time);

-- Index on sensor_data.tenant_id (covered by unique constraint, but explicit)
CREATE INDEX IF NOT EXISTS idx_sensor_data_tenant_id ON sensor_data(tenant_id);

-- Index on sensor_thresold.tenant_id (covered by PK, but explicit)
CREATE INDEX IF NOT EXISTS idx_sensor_thresold_tenant_id ON sensor_thresold(tenant_id);

-- Index on user_list.tenant_id for user authentication (covered by PK, but explicit)
CREATE INDEX IF NOT EXISTS idx_user_list_tenant_id ON user_list(tenant_id);

-- Index on sensor_list.tenant_id
CREATE INDEX IF NOT EXISTS idx_sensor_list_tenant_id ON sensor_list(tenant_id);

-- Step 13: Add foreign key constraints
-- ============================================================================
-- Foreign key from node to tenant
ALTER TABLE node
DROP CONSTRAINT IF EXISTS fk_node_tenant,
ADD CONSTRAINT fk_node_tenant
FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Foreign key from sensor_info to tenant
ALTER TABLE sensor_info
ADD CONSTRAINT fk_sensor_info_tenant
FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Foreign key from sensor_data to tenant
ALTER TABLE sensor_data
ADD CONSTRAINT fk_sensor_data_tenant
FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Foreign key from sensor_thresold to tenant
ALTER TABLE sensor_thresold
ADD CONSTRAINT fk_sensor_thresold_tenant
FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Foreign key from user_list to tenant
ALTER TABLE user_list
ADD CONSTRAINT fk_user_list_tenant
FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Foreign key from sensor_list to tenant
ALTER TABLE sensor_list
ADD CONSTRAINT fk_sensor_list_tenant
FOREIGN KEY (tenant_id) REFERENCES tenant(tenant_id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

-- Step 13: Make tenant_id NOT NULL (enforce data integrity)
-- ============================================================================
-- After migrating all data, make tenant_id mandatory

ALTER TABLE node
ALTER COLUMN tenant_id SET NOT NULL;

ALTER TABLE sensor_info
ALTER COLUMN tenant_id SET NOT NULL;

ALTER TABLE sensor_data
ALTER COLUMN tenant_id SET NOT NULL;

ALTER TABLE sensor_thresold
ALTER COLUMN tenant_id SET NOT NULL;

ALTER TABLE user_list
ALTER COLUMN tenant_id SET NOT NULL;

-- sensor_list can remain nullable if you want shared sensor types
-- Uncomment if you want to enforce tenant-specific sensor types:
-- ALTER TABLE sensor_list ALTER COLUMN tenant_id SET NOT NULL;

-- Step 14: Create sample test tenants (optional)
-- ============================================================================
-- Uncomment to create test tenants for testing multi-tenant isolation

-- INSERT INTO tenant (tenant_name, contact_email, is_active, remarks)
-- VALUES
--     ('Organization A', 'contact@orga.com', TRUE, 'Test tenant A'),
--     ('Organization B', 'contact@orgb.com', TRUE, 'Test tenant B'),
--     ('Test Organization', 'test@example.com', TRUE, 'Test organization')
-- RETURNING tenant_id, tenant_name;

-- Step 15: Verification queries
-- ============================================================================
-- Run these queries to verify the migration was successful

-- Check tenant table
SELECT COUNT(*) as tenant_count FROM tenant;

-- Check node table tenant_id distribution
SELECT tenant_id, COUNT(*) as node_count
FROM node
GROUP BY tenant_id;

-- Check sensor_data table tenant_id distribution
SELECT tenant_id, COUNT(*) as data_count
FROM sensor_data
GROUP BY tenant_id;

-- Verify all tables have tenant_id column
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE column_name = 'tenant_id'
    AND table_schema = 'public'
ORDER BY table_name;

-- Check indexes created
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE indexname LIKE '%tenant%'
ORDER BY tablename;

-- Check foreign key constraints
SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND kcu.column_name = 'tenant_id'
ORDER BY tc.table_name;

-- ============================================================================
-- Migration Complete!
-- ============================================================================
-- Next Steps:
-- 1. Test the NodeValue.py changes with sample sensor data
-- 2. Verify tenant isolation by creating test tenants and data
-- 3. Update Final_gui.py to add tenant selection dropdowns
-- 4. Update views.py to filter all queries by tenant_id
-- 5. Run performance tests on sensor_data queries with tenant_id
-- ============================================================================
