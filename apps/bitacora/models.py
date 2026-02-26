from sqlalchemy import ( Column, String, Index, Text)
from sqlalchemy.dialects.mysql import BIGINT, DATETIME, INTEGER
from sqlalchemy.sql import func, text
from core.database import Base

class AuditAdmin(Base):
    __tablename__ = "audit_admin"
    __table_args__ = (
        Index("ix_audit_admin_table_record", "table_name", "record_id"),
        Index("ix_audit_admin_action_created", "action", "created_at"),
        Index("ix_audit_admin_table_record_created", "table_name", "record_id", "created_at"),
        Index("ix_audit_admin_actor_created", "actor_id", "created_at"),
        Index("ix_audit_admin_event_id", "event_id"),
        Index("ix_audit_admin_event_created", "event_id", "created_at"),

        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Audit log for users resource",
        },
    )

    # PK (BIGINT AI)
    audit_id = Column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
        comment="Audit row id",
    )

    event_id = Column(
        String(32),
        nullable=True,
        comment="Correlation id for the audit event (uuid4().hex)",
    )

    # Actor (who performed the action) — sin FK para no bloquear deletes
    actor_id = Column(
        BIGINT(unsigned=True),
        nullable=True,
        comment="User id of the actor (who performed the action)",
    )

    created_at = Column(
        DATETIME(fsp=6),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP(6)"),
        comment="UTC timestamp",
    )

    view_id = Column(
        INTEGER(unsigned=True), 
        nullable=False,
        comment="Vista desde la cual se realizó la acción",
    )

    table_name = Column(
        String(128),
        nullable=False,
        comment="Target table/resource name (e.g. users)",
    )

    record_id = Column(
        BIGINT(unsigned=True),
        nullable=False,
        comment="Target record id (user_id)",
    )

    action = Column(
        String(16),
        nullable=False,
        comment="insert|update|delete|read|error",
    )

    field_name = Column(
        String(128),
        nullable=True,
        comment="Changed field name (for update/insert)",
    )

    value = Column(
        Text,
        nullable=True,
        comment="New value / '1' / JSON / etc",
    )

    meta = Column(
        Text,
        nullable=True,
        comment="JSON string with extra context (endpoint, view_id, error, etc.)",
    )

    ip_address = Column(
        String(45),
        nullable=True,
        comment="Client IP (v4/v6)",
    )