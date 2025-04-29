import asyncio
import logging
import sys

from os import getenv

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from handlers import get_routers
from middleware.users_middleware import UserMiddleware


async def main():
    bot = Bot(token=getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_routers(*get_routers())

    dp.message.outer_middleware(UserMiddleware())

    await dp.start_polling(bot)


if __name__ == "__main__":
    load_dotenv()

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
