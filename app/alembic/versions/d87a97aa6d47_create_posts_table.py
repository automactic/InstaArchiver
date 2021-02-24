"""create posts table

Revision ID: d87a97aa6d47
Revises: 8854736fb176
Create Date: 2020-11-11 17:42:51.365726

"""
from alembic import op
from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY


# revision identifiers, used by Alembic.
revision = 'd87a97aa6d47'
down_revision = '8854736fb176'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'posts',
        Column('shortcode', String, primary_key=True),
        Column('owner_username', String, ForeignKey('profiles.username'), index=True),
        Column('creation_time', DateTime, index=True, nullable=False),
        Column('type', String, index=True, nullable=False),
        Column('caption', String, index=True, nullable=True),
        Column('caption_hashtags', ARRAY(String), index=True, nullable=False),
        Column('caption_mentions', ARRAY(String), index=True, nullable=False),
    )


def downgrade():
    op.drop_table('posts')
