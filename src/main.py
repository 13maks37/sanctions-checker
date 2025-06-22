import asyncio
import logging
import logging.config
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from src.core.logger import logging_config
from src.keyboards.set_main_menu_bot import set_main_menu
from src.handlers import user_handlers
from src.db.connect import AsyncSessionLocal
from src.utils.middlewares import DBSessionMiddleware
from src.core.config import settings


logger = logging.getLogger(__name__)


async def main():
    logging.config.dictConfig(logging_config)
    logger.info("Starting BOTV")
    bot: Bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML"),
    )
    storage = RedisStorage.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )
    dp: Dispatcher = Dispatcher(storage=storage)
    await set_main_menu(bot)
    dp.update.middleware(DBSessionMiddleware(AsyncSessionLocal))
    dp.include_router(user_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"[Exception] - {e}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
