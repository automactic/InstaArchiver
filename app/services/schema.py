import os

import sqlalchemy
from sqlalchemy import MetaData, Table, Column, ForeignKey, Integer, String, Boolean, DateTime


def create_engine() -> sqlalchemy.engine.Engine:
    hostname = os.getenv('DATABASE_HOSTNAME', 'localhost')
    url = f'postgresql://postgres:postgres@{hostname}/insta_save'
    return sqlalchemy.create_engine(url)


def create_connection() -> sqlalchemy.engine.Connection:
    engine = create_engine()
    with engine.connect() as connection:
        yield connection


metadata = MetaData()

profiles = Table(
    'profiles',
    metadata,
    Column('username', String, primary_key=True),
    Column('full_name', String, index=True, nullable=False),
    Column('biography', String, index=True, nullable=True),
    Column('auto_update', Boolean, index=True, default=False),
    Column('last_update', DateTime, index=True, nullable=True),
)

posts = Table(
    'posts',
    metadata,
    Column('shortcode', String, primary_key=True),
    Column('owner_username', String, ForeignKey('profiles.username'), index=True),
    Column('creation_time', DateTime, index=True),
    Column('type', String, index=True),
    Column('caption', String, index=True, nullable=True),
)

post_items = Table(
    'post_items',
    metadata,
    Column('post_shortcode', String, ForeignKey('posts.shortcode'), primary_key=True),
    Column('index', Integer, primary_key=True),
    Column('type', String, index=True),
    Column('filename', String, index=True),
)