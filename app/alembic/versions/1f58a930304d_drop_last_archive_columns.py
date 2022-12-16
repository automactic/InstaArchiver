"""drop last_archive_columns

Revision ID: 1f58a930304d
Revises: 2a0330463fc9
Create Date: 2022-12-16 09:26:58.798833

"""
from alembic import op
from sqlalchemy import Column, DateTime


# revision identifiers, used by Alembic.
revision = '1f58a930304d'
down_revision = '2a0330463fc9'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('profiles', 'last_archive_timestamp')
    op.drop_column('profiles', 'last_archive_latest_post_timestamp')


def downgrade():
    op.add_column('profiles', Column('last_archive_timestamp', DateTime, index=True, nullable=True))
    op.add_column('profiles', Column('last_archive_latest_post_timestamp', DateTime, index=True, nullable=True))
