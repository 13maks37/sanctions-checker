import logging
import logging.config
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import User
from src.core.logger import logging_config


logging.config.dictConfig(logging_config)
logger = logging.getLogger("db_operations")


class BaseDAO:
    """Base class with operations on tables"""

    model = None

    @classmethod
    async def get_all(cls, session: AsyncSession):
        """Get all elements from a table"""
        try:
            logger.info(f"Fetching all records for {cls.model.__name__}")
            query = select(cls.model)
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(
                f"An error occurred while fetching all records for "
                f"{cls.model.__name__}: {e}",
            )
            raise e

    @classmethod
    async def get_by_id(cls, session: AsyncSession, id: int):
        """Get elements by id or return None if not"""
        try:
            logger.info(f"Fetching {cls.model.__name__} with id {id}")
            query = select(cls.model).where(cls.model.id == id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(
                f"An error occurred while fetching "
                f"{cls.model.__name__} with id {id}: {e}",
            )
            raise e

    @classmethod
    async def add(cls, session: AsyncSession, **values):
        """Add an object to the table"""
        new_instance = cls.model(**values)
        session.add(new_instance)
        try:
            await session.commit()
            logger.info(f"Added new {cls.model.__name__}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error adding {cls.model.__name__}: {e}")
            raise e
        return new_instance

    @classmethod
    async def update(cls, session: AsyncSession, id: int, **values):
        """Change elements for id"""
        logger.info(f"Updating {cls.model.__name__} with id {id}")
        instance = await cls.get_by_id(session, id)
        if not instance:
            logger.warning(f"{cls.model.__name__} with id {id} not found")
            return None

        for key, value in values.items():
            setattr(instance, key, value)

        try:
            await session.commit()
            logger.info(f"Updated {cls.model.__name__} with id {id}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating {cls.model.__name__}: {e}")
            raise e
        return instance

    @classmethod
    async def delete(cls, session: AsyncSession, id: int):
        """Delete by id"""
        logger.info(f"Deleting {cls.model.__name__} with id {id}")
        try:
            data = await cls.get_by_id(session=session, id=id)
            if data:
                await session.delete(data)
                await session.commit()
                logger.info(f"Deleted {cls.model.__name__} with id {id}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting {cls.model.__name__}: {e}")
            raise e


class UserDAO(BaseDAO):
    """Class with operations for User model"""

    model = User

    @classmethod
    async def get_by_tg_id(cls, session: AsyncSession, tg_id: str):
        """Get User elements by tg_id"""
        try:
            logger.info("Fetching User by Telegram ID")
            query = select(cls.model).where(cls.model.tg_id == tg_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(
                f"An error occurred while fetching User by Telegram ID: {e}",
            )
            raise e
