from dotenv import load_dotenv
from typing import Dict, Any, Awaitable, Callable
from json import loads
from os import getenv

from aiogram.types import TelegramObject, Message
from aiogram import BaseMiddleware


class UserMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]) -> Any:
        user = data['event_from_user']
        print(user.id)
        bitrix_user_id = dict(loads(getenv("USERS"))).get(str(user.id))
        if not (type(event) is Message) or bitrix_user_id:
            data["bitrix_user_id"] = bitrix_user_id
            return await handler(event, data)

        await event.bot.send_message(user.id, "❗Отказ в доступе на использование бота❗")



