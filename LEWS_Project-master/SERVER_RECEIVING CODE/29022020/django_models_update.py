# ============================================================================
# Django Models Update for Multi-Tenant Support
# ============================================================================
# Add these models to: c:\Users\MM_Lab_RKP_PC_1\Desktop\site\01022021_website\user_entry\login\models.py
#
# INSTRUCTIONS:
# 1. Open models.py
# 2. Add the Tenant and UStatus models below to the file
# 3. Update existing models to include tenant_id foreign keys
# 4. Run: python manage.py makemigrations
# 5. Run: python manage.py migrate
# ============================================================================

from django.db import models


# ============================================================================
# NEW MODEL: Tenant
# ============================================================================
class Tenant(models.Model):
    """
    Tenant/Organization master table for multi-tenant architecture
    """
    tenant_id = models.AutoField(primary_key=True)
    tenant_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    contact_email = models.CharField(max_length=100, blank=True, null=True)
    settings = models.JSONField(blank=True, null=True)  # Requires PostgreSQL or Django 3.1+
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        managed = False  # Set to True if you want Django to manage this table
        db_table = 'tenant'
        ordering = ['tenant_id']

    def __str__(self):
        return f"{self.tenant_name} (ID: {self.tenant_id})"


# ============================================================================
# NEW MODEL: UStatus
# ============================================================================
class UStatus(models.Model):
    """
    User-location access control table
    Maps which users have access to which locations within their tenant
    """
    # Composite unique: (tenant_id, email_id, location)
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id')
    email_id = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    node_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False  # Set to True if you want Django to manage this table
        db_table = 'u_status'
        unique_together = (('tenant', 'email_id', 'location'),)

    def __str__(self):
        return f"{self.email_id} @ {self.location} (Tenant: {self.tenant_id})"


# ============================================================================
# UPDATED MODELS: Add tenant_id foreign keys
# ============================================================================

class Node(models.Model):
    """
    UPDATED: Added tenant foreign key and composite unique constraint
    """
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id')  # NEW
    name = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    node_id = models.CharField(primary_key=True, max_length=100)
    remark = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'node'
        unique_together = (('tenant', 'node_id'),)  # NEW: Composite unique constraint

    def __str__(self):
        return f"{self.node_id} @ {self.location}"


class SensorInfo(models.Model):
    """
    UPDATED: Changed primary key to composite (tenant_id, sensor_id)
    """
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id')  # NEW
    sensor_id = models.CharField(max_length=100)
    sensor_type = models.CharField(max_length=100, blank=True, null=True)
    node = models.ForeignKey(Node, models.DO_NOTHING, blank=True, null=True)
    depth = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    remark = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensor_info'
        unique_together = (('tenant', 'sensor_id'),)  # UPDATED: Composite PK

    def __str__(self):
        return f"{self.sensor_id} ({self.sensor_type})"


class SensorData(models.Model):
    """
    UPDATED: Added tenant and updated unique constraint to 3-column composite
    """
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id')  # NEW
    sensor = models.ForeignKey(SensorInfo, models.DO_NOTHING, db_column='sensor_id')
    sensor_value = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    receive_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sensor_data'
        unique_together = (('tenant', 'sensor', 'receive_time'),)  # UPDATED: 3-column unique

    def __str__(self):
        return f"{self.sensor_id} = {self.sensor_value} @ {self.receive_time}"


class SensorThresold(models.Model):
    """
    UPDATED: Changed primary key to composite (tenant_id, sensor_id)
    """
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id')  # NEW
    sensor = models.ForeignKey(SensorInfo, models.DO_NOTHING, db_column='sensor_id')
    min_value = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    max_value = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    last_email = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensor_thresold'
        unique_together = (('tenant', 'sensor'),)  # UPDATED: Composite PK

    def __str__(self):
        return f"Thresholds for {self.sensor_id}: {self.min_value}-{self.max_value}"


class UserList(models.Model):
    """
    UPDATED: Changed primary key to composite (tenant_id, email_id)
    """
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id')  # NEW
    uname = models.CharField(max_length=100, blank=True, null=True)
    upassword = models.CharField(max_length=100, blank=True, null=True)
    ph_no = models.CharField(max_length=100, blank=True, null=True)
    email_id = models.CharField(max_length=100)
    user_type = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    verify = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_list'
        unique_together = (('tenant', 'email_id'),)  # UPDATED: Composite PK

    def __str__(self):
        return f"{self.uname} ({self.email_id}) - Tenant {self.tenant_id}"


class SensorList(models.Model):
    """
    UPDATED: Added optional tenant foreign key (can be shared or per-tenant)
    """
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id', blank=True, null=True)  # NEW (Optional)
    sensor_name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensor_list'

    def __str__(self):
        return self.sensor_name or "Unnamed Sensor"


# ============================================================================
# QUERY HELPER METHODS
# ============================================================================

class TenantQuerySet(models.QuerySet):
    """
    Custom queryset for tenant-aware filtering
    """
    def for_tenant(self, tenant_id):
        """Filter queryset by tenant_id"""
        return self.filter(tenant_id=tenant_id)


# Usage examples:
# Node.objects.filter(tenant_id=1)
# SensorData.objects.filter(tenant_id=1, receive_time__gte=start_date)
# UserList.objects.get(tenant_id=1, email_id='user@example.com')

# ============================================================================
# MIGRATION NOTES
# ============================================================================
"""
After adding these models to models.py:

1. Create migrations:
   python manage.py makemigrations login

2. Review the migration file:
   Check: c:/Users/MM_Lab_RKP_PC_1/Desktop/site/01022021_website/user_entry/login/migrations/

3. Apply migrations:
   python manage.py migrate

4. Verify in database:
   SELECT table_name, column_name FROM information_schema.columns
   WHERE column_name = 'tenant_id' AND table_schema = 'public';

IMPORTANT:
- Since managed=False, Django won't create/modify these tables
- Run the SQL migration script (migration_add_tenant_id.sql) first
- Then update models.py to match the schema
- Django migrations will only update the ORM, not the database

If you want Django to manage the tables:
- Change managed=False to managed=True
- Remove the manual SQL migration script
- Let Django create the tables via migrations
"""
