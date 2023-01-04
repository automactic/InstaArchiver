"""add time range columns in tasks table

Revision ID: c5521d5c2307
Revises: 16128ba515fe
Create Date: 2023-01-04 08:40:34.267535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5521d5c2307'
down_revision = '16128ba515fe'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tasks', sa.Column('time_range_start', sa.DateTime(), nullable=True))
    op.add_column('tasks', sa.Column('time_range_end', sa.DateTime(), nullable=True))
    op.alter_column('tasks', 'type', nullable=False)


def downgrade():
    op.alter_column('tasks', 'type', nullable=True)
    op.drop_column('tasks', 'time_range_end')
    op.drop_column('tasks', 'time_range_start')
