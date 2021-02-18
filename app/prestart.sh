#! /usr/bin/env bash

# temp fix: downgrade sqlalchemy
pip install SQLAlchemy==1.3.23
# Let the DB start
sleep 10;
# Run migrations
alembic upgrade head
# temp fix: upgrade sqlalchemy
pip install SQLAlchemy==1.4.0b3