from django.db import models

class AuditAdmin(models.Model):
    audit_id = models.BigAutoField(primary_key=True)

    event_id = models.CharField(max_length=32, null=True)
    actor_id = models.BigIntegerField(null=True)

    created_at = models.DateTimeField()
    view_id = models.PositiveIntegerField()

    table_name = models.CharField(max_length=128)
    record_id = models.BigIntegerField()

    action = models.CharField(max_length=16)
    field_name = models.CharField(max_length=128, null=True)
    value = models.TextField(null=True)
    meta = models.TextField(null=True)

    ip_address = models.CharField(max_length=45, null=True)

    class Meta:
        db_table = "audit_admin"
        managed = False  