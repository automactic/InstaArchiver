"""create post_items table

Revision ID: 2a0330463fc9
Revises: d87a97aa6d47
Create Date: 2020-11-11 18:08:24.406396

"""
from alembic import op
from sqlalchemy import Column, Float, ForeignKey, Integer, String


# revision identifiers, used by Alembic.
revision = '2a0330463fc9'
down_revision = 'd87a97aa6d47'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'post_items',
        Column('post_shortcode', String, ForeignKey('posts.shortcode'), primary_key=True),
        Column('index', Integer, primary_key=True),
        Column('type', String, index=True, nullable=False),
        Column('duration', Float, index=True, nullable=True),
        Column('filename', String, index=True, nullable=False),
        Column('thumb_image_filename', String, nullable=True),
    )


def downgrade():
    op.drop_table('post_items')
