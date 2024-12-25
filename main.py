import asyncio
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties

from configuration import settings
from loguru import logger

from handlers import reply_handler

logger.add("debug.log", format="{time} : {level} :: {message}", level="DEBUG", rotation="10 MB", compression="zip")


async def start_bot():
    bot = Bot(settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    # import routers
    dp.include_routers(
        reply_handler.router
    )

    #start bot's webhook
    bot_info = await bot.get_me()
    logger.info(f"Бот @{bot_info.username} (ID: {bot_info.id}) запущен.")
    await bot.delete_webhook()
    await dp.start_polling(bot)


async def starter():
    await asyncio.gather(start_bot())


if __name__ == "__main__":
    asyncio.run(starter())
