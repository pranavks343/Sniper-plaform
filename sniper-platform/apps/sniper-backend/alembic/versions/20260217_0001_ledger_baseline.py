"""Create production ledger baseline with schema namespaces

Revision ID: 20260217_0001
Revises:
Create Date: 2026-02-17 22:30:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

from app.models.database.base import Base
from app.models.database.namespaces import ALL_SCHEMAS

# Ensure model tables are loaded into metadata.
import app.models.database  # noqa: F401

# revision identifiers, used by Alembic.
revision = '20260217_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    for schema in ALL_SCHEMAS:
        bind.execute(sa.text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))

    Base.metadata.create_all(bind=bind)

    # Best-effort Timescale setup. Works when extension is available; safely no-ops otherwise.
    bind.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_available_extensions WHERE name = 'timescaledb') THEN
                    CREATE EXTENSION IF NOT EXISTS timescaledb;
                END IF;
            END
            $$;
            """
        )
    )
    bind.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
                    PERFORM create_hypertable('portfolio.position_snapshots', 'as_of', if_not_exists => TRUE, migrate_data => TRUE);
                    PERFORM create_hypertable('analytics.pnl_intraday', 'as_of', if_not_exists => TRUE, migrate_data => TRUE);
                END IF;
            END
            $$;
            """
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
    for schema in reversed(ALL_SCHEMAS):
        bind.execute(sa.text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
