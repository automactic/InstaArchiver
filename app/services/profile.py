import sqlalchemy as sa

from services import schema


class ProfileService:
    def __init__(self, connection: sa.engine.Connection):
        self.connection = connection

    async def exists(self, username: str) -> bool:
        """Check if a profile exists.

        :param username: username of the profile to check
        """

        statement = schema.profiles.select().where(schema.profiles.c.username == username)
        exists_statement = sa.select([sa.exists(statement)])
        return await self.connection.execute(exists_statement).scalar()
