"""Add performance indexes

Revision ID: a1b2c3d4e5f6
Revises: c932eb470946
Create Date: 2026-03-10 16:47:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'c932eb470946'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add indexes on columns used in ORDER BY and WHERE clauses."""
    # Indexes on createdAt for ORDER BY DESC queries
    op.create_index('ix_contacts_createdAt', 'contacts', ['createdAt'])
    op.create_index('ix_deals_createdAt', 'deals', ['createdAt'])
    op.create_index('ix_tasks_createdAt', 'tasks', ['createdAt'])
    op.create_index('ix_notes_createdAt', 'notes', ['createdAt'])

    # Index on sentAt for emails ORDER BY DESC
    op.create_index('ix_emails_sentAt', 'emails', ['sentAt'])

    # Index on activity time for ORDER BY DESC LIMIT
    op.create_index('ix_activity_time', 'activity', ['time'])


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index('ix_activity_time', table_name='activity')
    op.drop_index('ix_emails_sentAt', table_name='emails')
    op.drop_index('ix_notes_createdAt', table_name='notes')
    op.drop_index('ix_tasks_createdAt', table_name='tasks')
    op.drop_index('ix_deals_createdAt', table_name='deals')
    op.drop_index('ix_contacts_createdAt', table_name='contacts')
