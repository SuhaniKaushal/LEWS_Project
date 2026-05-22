# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# UPDATED: Added multi-tenant support with Tenant and UStatus models
from django.db import models


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


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


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
