"""create profiles table

Revision ID: 8854736fb176
Revises: 
Create Date: 2020-11-08 16:46:40.601392

"""
from alembic import op
from sqlalchemy import Column, String


# revision identifiers, used by Alembic.
revision = '8854736fb176'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'profiles',
        Column('username', String, primary_key=True),
        Column('full_name', String, nullable=False),
        Column('biography', String, nullable=True),
    )


def downgrade():
    op.drop_table('profiles')
