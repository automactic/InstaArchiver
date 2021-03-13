import os

import sqlalchemy
from sqlalchemy import MetaData, Table, Column, ForeignKey, Integer, Float, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import ARRAY

database_hostname = os.getenv('DATABASE_HOSTNAME', 'localhost')
database_url = f'postgresql://postgres:postgres@{database_hostname}/insta_archiver'


def create_engine() -> sqlalchemy.engine.Engine:
    return sqlalchemy.create_engine(database_url)


async def create_connection() -> sqlalchemy.engine.Connection:
    engine = create_engine()
    with engine.connect() as connection:
        yield connection


metadata = MetaData()

profiles = Table(
    'profiles',
    metadata,
    Column('username', String, primary_key=True),
    Column('full_name', String, index=True, nullable=False),
    Column('display_name', String, index=True, nullable=False),
    Column('biography', String, index=True, nullable=True),
    Column('image_filename', String, index=True, nullable=False),
    Column('auto_archive', Boolean, index=True, nullable=False),
    Column('last_archive_timestamp', DateTime, index=True, nullable=True),
    Column('last_archive_latest_post_timestamp', DateTime, index=True, nullable=True),
)

posts = Table(
    'posts',
    metadata,
    Column('shortcode', String, primary_key=True),
    Column('username', String, ForeignKey('profiles.username'), index=True),
    Column('timestamp', DateTime, index=True, nullable=False),
    Column('type', String, index=True, nullable=False),
    Column('caption', String, index=True, nullable=True),
    Column('caption_hashtags', ARRAY(String), index=True, nullable=False),
    Column('caption_mentions', ARRAY(String), index=True, nullable=False),
)

post_items = Table(
    'post_items',
    metadata,
    Column('shortcode', String, ForeignKey('posts.shortcode'), primary_key=True),
    Column('index', Integer, primary_key=True),
    Column('type', String, index=True, nullable=False),
    Column('duration', Float, index=True, nullable=True),
    Column('filename', String, index=True, nullable=False),
    Column('thumb_image_filename', String, nullable=True),
)
