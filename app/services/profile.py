import sqlalchemy as sa

from . import schema
from .base import BaseService


class ProfileService(BaseService):
    def exists(self, username: str, connection: sa.engine.Connection) -> bool:
        """Check if a profile exists.

        :param username: username of the profile to check
        """

        statement = schema.profiles.select().where(schema.profiles.c.username == username)
        exists_statement = sa.select([sa.exists(statement)])
        return connection.execute(exists_statement).scalar()
