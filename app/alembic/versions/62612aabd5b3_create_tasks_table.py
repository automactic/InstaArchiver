"""create tasks table

Revision ID: 62612aabd5b3
Revises: 1f58a930304d
Create Date: 2022-12-31 16:09:46.908573

"""
from alembic import op
from sqlalchemy import Column, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '62612aabd5b3'
down_revision = '1f58a930304d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tasks',
        Column('id', UUID(as_uuid=True), primary_key=True),
        Column('username', String, ForeignKey('profiles.username', ondelete='CASCADE'), index=True, nullable=True),
        Column('type', String, index=True),
        Column('status', String, index=True, nullable=False),
        Column('created', DateTime, index=True, nullable=False),
        Column('started', DateTime, nullable=True),
        Column('completed', DateTime, nullable=True),
    )


def downgrade():
    op.drop_table('tasks')
