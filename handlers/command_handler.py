from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from kbs.keyboards_user import main_kb

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer("Здравствуйте, ваш аккаунт успешно связан с битрикс", reply_markup=main_kb())

