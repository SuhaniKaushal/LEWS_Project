# Multi-Tenant Migration Implementation Guide

## ⚠️ IMPORTANT: Data Format Change

**tenant_id is now an INTEGER (auto-increment), not a VARCHAR!**

### Old Data Format:
```
tenantId@location@coordinator@node(sensor:value)...
Example: default@c1@netala@n1(moisture1:581.02)
```

### New Data Format (INTEGER tenant_id):
```
tenantId@location@coordinator@node(sensor:value)...
Example: 1@c1@netala@n1(moisture1:581.02)
```

The first tenant created will have tenant_id=1, second will be 2, etc.

---

## Summary of Changes

### ✅ Completed Changes to NodeValue.py

#### 1. Updated `get_node_id()` Method (Line 35-49)
**What Changed:**
- Added `tenantId` parameter to method signature
- Fixed SQL injection vulnerability by using parameterized query
- Added `tenant_id` filter to WHERE clause

**Before:**
```python
def get_node_id(self, cname, name):
    query = "select node_id from node where name='"+name+"' and location='"+cname+"'"
    cursor.execute(query)
```

**After:**
```python
def get_node_id(self, cname, name, tenantId):
    query = "SELECT node_id FROM node WHERE name=%s AND location=%s AND tenant_id=%s"
    cursor.execute(query, (name, cname, tenantId))
```

#### 2. Updated `sensorvalues()` Method Call (Line 91)
**What Changed:**
- Pass `tenantId` to `get_node_id()` method

**Before:**
```python
node_id = self.get_node_id(coordinator_name, node_name)
```

**After:**
```python
node_id = self.get_node_id(coordinator_name, node_name, tenantId)
```

#### 3. Updated INSERT Query for sensor_data (Line 179-181)
**What Changed:**
- Added `tenant_id` column to INSERT statement
- Included `tenantId` value in record tuple

**Before:**
```python
postgres_insert_query = 'INSERT INTO sensor_data (sensor_id,sensor_value,receive_time) VALUES (%s,%s,%s)'
record_to_insert = (id, value, s5)
```

**After:**
```python
postgres_insert_query = 'INSERT INTO sensor_data (tenant_id,sensor_id,sensor_value,receive_time) VALUES (%s,%s,%s,%s)'
record_to_insert = (tenantId, id, value, s5)
```

---

## Database Migration Steps

### Step 1: Backup Your Database
```bash
pg_dump -U postgres -d netala_database > backup_$(date +%Y%m%d).sql
```

### Step 2: Run Migration Script
```bash
psql -U postgres -d netala_database -f migration_add_tenant_id.sql
```

### Step 3: Verify Migration
After running the script, check the verification queries at the end of the SQL file to confirm:
- ✅ tenant table created
- ✅ tenant_id columns added to all tables
- ✅ Indexes created
- ✅ Foreign key constraints added
- ✅ Existing data migrated to 'default' tenant

---

## Database Schema Changes

### Tenant Master Table (NEW)
```sql
CREATE TABLE tenant (
    tenant_id SERIAL PRIMARY KEY,          -- Auto-increment integer
    tenant_name VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    contact_email VARCHAR(100),
    settings JSONB,                        -- JSON config per tenant
    remarks TEXT
);
```

### Composite Unique Constraints Added

All tenant-specific tables now have composite unique constraints to ensure data isolation:

| Table | Composite Unique Constraint | Purpose |
|-------|---------------------------|---------|
| `user_list` | `(tenant_id, email_id)` | Email unique per tenant |
| `node` | `(tenant_id, node_id)` | Node ID unique per tenant |
| `sensor_info` | `(tenant_id, sensor_id)` | Sensor ID unique per tenant |
| `sensor_data` | `(tenant_id, sensor_id, receive_time)` | One reading per sensor per time per tenant |
| `sensor_thresold` | `(tenant_id, sensor_id)` | One threshold config per sensor per tenant |
| `u_status` | `(tenant_id, email_id, location)` | User-location mapping per tenant |

### Data Format Changes

**⚠️ CRITICAL: tenant_id is now INTEGER, not string!**

### Old Format (3 parts):
```
location@coordinator@node(sensor:value)(sensor:value)...
```
Example:
```
c1@netala@n1(moisture1:581.02)(pitch10:-75)
```

### New Format (4 parts - with INTEGER tenant_id):
```
tenantId@location@coordinator@node(sensor:value)(sensor:value)...
```
Example:
```
1@c1@netala@n1(moisture1:581.02)(pitch10:-75)
```

**Important Notes:**
- tenant_id is an **integer** (1, 2, 3...), not a string ("default", "org_a")
- First tenant created will have tenant_id = 1
- Your sensor data transmitters/clients must send the numeric tenant_id!

---

## Testing the Changes

### Option 1: Test with NodeValue.py Standalone
```bash
cd "c:\Users\MM_Lab_RKP_PC_1\Desktop\site\SERVER_RECEIVING CODE\29022020"
python NodeValue.py
```

This will run the test case at the bottom of the file with the sample data:
```python
ContentFromClient("default@c1@netala@n1(moisture1:581.02)(pitch10:-75)...")
```

### Option 2: Test with Net.py Server
1. Ensure the database migration is complete
2. Start Net.py server:
```bash
python Net.py
```
3. Send test data via TCP socket with the new format:
```
default@c1@netala@n1(moisture1:581.02)(pitch10:-75)(roll1:-4)
```

### Option 3: Verify Database Queries
```sql
-- Check that tenant_id is being stored
SELECT tenant_id, sensor_id, sensor_value, receive_time
FROM sensor_data
ORDER BY receive_time DESC
LIMIT 10;

-- Check tenant isolation works
SELECT tenant_id, COUNT(*) as record_count
FROM sensor_data
GROUP BY tenant_id;
```

---

## Creating New Tenants

### 1. Add New Tenant to Database
```sql
INSERT INTO tenant (tenant_name, contact_email, is_active, remarks)
VALUES ('Organization A', 'contact@orga.com', TRUE, 'Production tenant for Org A')
RETURNING tenant_id;

-- Returns: tenant_id = 2 (for example)
```

### 2. Create Nodes for the Tenant
```sql
INSERT INTO node (tenant_id, name, location, node_id, remark)
VALUES (2, 'n1', 'netala', 'n1', 'Node 1 for Organization A');
```

### 3. Create Sensor Info for the Tenant
```sql
INSERT INTO sensor_info (tenant_id, sensor_id, sensor_type, node_id, depth, remark)
VALUES (2, 'n1_ms1', 'moisture', 'n1', 10, 'Moisture sensor at 10m depth');
```

### 4. Assign Users to the Tenant
```sql
-- For new users
INSERT INTO user_list (tenant_id, email_id, uname, upassword, user_type, status, verify)
VALUES (2, 'user@orga.com', 'John Doe', 'hashedpassword', 'USER', 'accepted', 'yes');

-- For existing users (change their tenant)
UPDATE user_list
SET tenant_id = 2
WHERE email_id = 'user@orga.com' AND tenant_id = 1;
```

### 5. Send Sensor Data for the Tenant
Use the new data format with the **integer** tenant_id:
```
2@netala@n1(moisture1:581.02)(pitch10:-75)
```

**Note**: The tenant_id is the integer returned from step 1!

---

## Troubleshooting

### Error: "column tenant_id does not exist"
**Cause:** Database migration not completed
**Solution:** Run the migration script: `migration_add_tenant_id.sql`

### Error: "PROBLEM IN FETCH node ID"
**Cause:** Node not found for the given tenant_id, location, and name
**Solution:** Check that:
1. The node exists in the database
2. The tenant_id matches
3. The location and name are correct

```sql
-- Check if node exists
SELECT * FROM node
WHERE name='n1' AND location='netala' AND tenant_id='default';
```

### Error: "insert or update on table violates foreign key constraint"
**Cause:** Referenced tenant_id doesn't exist in tenant table
**Solution:** Create the tenant first:
```sql
INSERT INTO tenant (tenant_id, tenant_name)
VALUES ('your_tenant_id', 'Your Tenant Name');
```

### Data Format Error
**Symptom:** getTenantId() returns wrong value or parsing fails
**Solution:** Ensure data format is correct:
- Must start with tenant_id
- Use @ as separator
- Format: `tenantId@location@coordinator@node(sensors)`

---

## Next Steps

### 1. Update Net.py (if needed)
If your sensor clients send data in the old 3-part format, you need to:
- Update clients to send tenant_id
- OR modify Net.py to prepend a default tenant_id before calling NodeValue

### 2. Update Final_gui.py
Add tenant selection to the GUI:
- Tenant dropdown in forms
- Filter queries by tenant_id
- See plan file for detailed changes

### 3. Update views.py
Add tenant filtering to web application:
- Get tenant_id from user session
- Filter all queries by tenant_id
- See plan file for 21 queries to update

### 4. Testing Multi-Tenant Isolation
Create test scenario:
1. Create 2 tenants: tenant_a, tenant_b
2. Create nodes for each tenant
3. Send sensor data for both tenants
4. Verify data isolation:
```sql
-- Should only show tenant_a data
SELECT * FROM sensor_data WHERE tenant_id = 'tenant_a';

-- Should only show tenant_b data
SELECT * FROM sensor_data WHERE tenant_id = 'tenant_b';

-- Should NOT return mixed results
SELECT sensor_id, tenant_id FROM sensor_data
WHERE sensor_id LIKE 'tenant_a%' AND tenant_id = 'tenant_b';
-- Expected: 0 rows
```

---

## Security Improvements Implemented

✅ **SQL Injection Fixed** in NodeValue.py:
- Query 1 (get_node_id): Now uses parameterized query
- Query 2 (insert sensor_data): Already parameterized, now includes tenant_id

❌ **Still Need to Fix** (for future work):
- Final_gui.py: Line 130 (SQL injection)
- views.py: Multiple locations (7+ SQL injection vulnerabilities)
- Password hashing: Plain text passwords in user_list table

---

## Performance Considerations

### Indexes Created
- `idx_node_tenant_id` - Fast node lookups by tenant
- `idx_sensor_info_tenant_id` - Fast sensor info lookups
- `idx_sensor_data_tenant_time` - **Critical** for time-series queries
- `idx_user_list_tenant_id` - Fast user authentication

### Query Performance Tips
- Always include `tenant_id` in WHERE clauses
- Use the composite index on sensor_data (tenant_id, receive_time) for time-range queries
- Monitor slow queries: `pg_stat_statements`

### Expected Performance Impact
- Minimal impact on small datasets (<100K records per tenant)
- Significant improvement for large multi-tenant deployments
- Index on (tenant_id, receive_time) enables fast time-series queries per tenant

---

## Django Models Update

### New Models Added

Two new models need to be added to `models.py`:

#### 1. Tenant Model (Master Table)
```python
class Tenant(models.Model):
    tenant_id = models.AutoField(primary_key=True)
    tenant_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)
    settings = models.JSONField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tenant'
```

#### 2. UStatus Model (User-Location Access Control)
```python
class UStatus(models.Model):
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id')
    email_id = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    node_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'u_status'
        unique_together = (('tenant', 'email_id', 'location'),)
```

**Note**: The `u_status` table is referenced in code (views.py) but was NOT previously defined in models.py. It has now been added.

### Updated Existing Models

All existing models need tenant_id foreign keys added:
- `Node` - Added tenant FK and composite unique
- `SensorInfo` - Changed PK to composite (tenant_id, sensor_id)
- `SensorData` - Changed unique constraint to (tenant_id, sensor_id, receive_time)
- `SensorThresold` - Changed PK to composite (tenant_id, sensor_id)
- `UserList` - Changed PK to composite (tenant_id, email_id)
- `SensorList` - Added optional tenant FK

**See**: `django_models_update.py` for complete updated models code.

---

## Files Modified

1. ✅ **NodeValue.py** - 3 changes (2 queries + 1 method signature)
2. ✅ **migration_add_tenant_id.sql** - Complete migration script with composite constraints
3. ✅ **TENANT_MIGRATION_GUIDE.md** - This documentation
4. ✅ **django_models_update.py** - Django ORM models for Tenant and UStatus + updated existing models

## Files Still Need Changes (Future Work)

1. ❌ **Net.py** - May need update if clients don't send tenant_id
2. ❌ **Final_gui.py** - 6 queries + tenant UI dropdown
3. ❌ **views.py** - 21 queries + session handling
4. ❌ **models.py** - Apply changes from django_models_update.py

---

## Support & References

- Full analysis and plan: `C:\Users\MM_Lab_RKP_PC_1\.claude\plans\wise-growing-pine.md`
- Migration script: `migration_add_tenant_id.sql`
- Modified code: `NodeValue.py`

For questions or issues, refer to the detailed plan document which includes:
- All 21 database queries with locations
- Complete schema analysis
- Step-by-step migration strategy
- Code examples for all changes
