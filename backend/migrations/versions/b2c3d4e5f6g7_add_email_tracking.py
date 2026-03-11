"""Add email tracking columns

Revision ID: b2c3d4e5f6g7
Revises: 53a5476bff3e
Create Date: 2026-03-11 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, Sequence[str], None] = '53a5476bff3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add email tracking columns for open tracking, read receipts, and inbox sync."""
    op.add_column('emails', sa.Column('trackingId', sa.String(), nullable=True))
    op.add_column('emails', sa.Column('openCount', sa.Integer(), server_default='0', nullable=True))
    op.add_column('emails', sa.Column('lastOpenedAt', sa.DateTime(), nullable=True))
    op.add_column('emails', sa.Column('isRead', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('emails', sa.Column('readAt', sa.DateTime(), nullable=True))
    op.add_column('emails', sa.Column('direction', sa.String(), server_default='sent', nullable=True))
    op.add_column('emails', sa.Column('contactId', sa.String(), nullable=True))
    op.add_column('emails', sa.Column('type', sa.String(), nullable=True))

    # Index for tracking pixel lookups
    op.create_index('ix_emails_trackingId', 'emails', ['trackingId'])
    op.create_index('ix_emails_direction', 'emails', ['direction'])
    op.create_index('ix_emails_contactId', 'emails', ['contactId'])


def downgrade() -> None:
    """Remove email tracking columns."""
    op.drop_index('ix_emails_contactId', table_name='emails')
    op.drop_index('ix_emails_direction', table_name='emails')
    op.drop_index('ix_emails_trackingId', table_name='emails')
    op.drop_column('emails', 'type')
    op.drop_column('emails', 'contactId')
    op.drop_column('emails', 'direction')
    op.drop_column('emails', 'readAt')
    op.drop_column('emails', 'isRead')
    op.drop_column('emails', 'lastOpenedAt')
    op.drop_column('emails', 'openCount')
    op.drop_column('emails', 'trackingId')
