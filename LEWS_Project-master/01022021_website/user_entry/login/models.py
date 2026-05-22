from django.db import models

# Create your models here.

class Tenant(models.Model):
    """Multi-tenant master table"""
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

    def __str__(self):
        return f"{self.tenant_name} (ID: {self.tenant_id})"


class UStatus(models.Model):
    """User-location access control table"""
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id')
    email_id = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    node_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'u_status'
        unique_together = (('tenant', 'email_id', 'location'),)

    def __str__(self):
        return f"{self.email_id} @ {self.location} (Tenant: {self.tenant_id})"


class Node(models.Model):
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id')
    name = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    node_id = models.CharField(primary_key=True, max_length=100)
    remark = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'node'
        unique_together = (('tenant', 'node_id'),)


class SensorData(models.Model):
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id')
    sensor = models.ForeignKey('SensorInfo', models.DO_NOTHING, db_column='sensor_id')
    sensor_value = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    receive_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'sensor_data'
        unique_together = (('tenant', 'sensor', 'receive_time'),)


class SensorInfo(models.Model):
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id')
    sensor_id = models.CharField(max_length=100)
    sensor_type = models.CharField(max_length=100, blank=True, null=True)
    node = models.ForeignKey(Node, models.DO_NOTHING, blank=True, null=True)
    depth = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    remark = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensor_info'
        unique_together = (('tenant', 'sensor_id'),)


class SensorList(models.Model):
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id', blank=True, null=True)
    sensor_name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensor_list'


class SensorThresold(models.Model):
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id')
    sensor = models.ForeignKey(SensorInfo, models.DO_NOTHING, db_column='sensor_id')
    min_value = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    max_value = models.DecimalField(max_digits=65535, decimal_places=65535, blank=True, null=True)
    last_email = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensor_thresold'
        unique_together = (('tenant', 'sensor'),)


class UserList(models.Model):
    tenant = models.ForeignKey(Tenant, models.DO_NOTHING, db_column='tenant_id')
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
        unique_together = (('tenant', 'email_id'),)
