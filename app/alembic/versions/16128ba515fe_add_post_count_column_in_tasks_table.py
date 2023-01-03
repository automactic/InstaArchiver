"""add post count column in tasks table

Revision ID: 16128ba515fe
Revises: 62612aabd5b3
Create Date: 2023-01-02 14:57:12.046116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16128ba515fe'
down_revision = '62612aabd5b3'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tasks', sa.Column('post_count', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('tasks', 'post_count')
