from aiogram import F
from aiogram import Router
from aiogram.types import Message

from bitrix_manager.bitrix24_manager import AsyncBitrixManager
from kbs.keyboards_user import create_creator_list


router = Router()

async_bx = AsyncBitrixManager()


@router.message(F.text == "Заказчики")
async def tasks_list_handler(message: Message, bitrix_user_id) -> None:

    customers_info = await async_bx.get_task_customer(bitrix_user_id)
    reply_m = create_creator_list(customers_info, bitrix_user_id)

    customer_text = ("Выберите заказчика"
                     if reply_m.inline_keyboard != [[]]
                    else "На данный момент активных заказов не найдено")

    await message.answer(customer_text,
                         reply_markup=reply_m)
