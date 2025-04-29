from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bitrix_manager.bitrix24_manager import AsyncBitrixManager
from kbs.keyboards_user import edit_task_kb
from utils.utils import send_tasks

router = Router()

async_bx = AsyncBitrixManager()


@router.callback_query(F.data.startswith("get_creator_task"))
async def creator_task_callback(callback: CallbackQuery, state: FSMContext):
    args = callback.data.split(" ")
    creator_id, user_id = map(int, args)

    tasks = await async_bx.get_task_by_group(user_id, creator_id)
    await state.update_data(button_info=[user_id, creator_id], task_count=len(tasks))

    await send_tasks(tasks, callback.message, state)


@router.callback_query(F.data.startswith("start_task", 'complete_task'))
async def interact_task_callback(callback: CallbackQuery):
    action = callback.data.split('_')[0]

    task_id = int(callback.data.split(" ")[1])

    await async_bx.interact_task(task_id, action)
    await callback.answer(f"Task {action}")

    await callback.message.delete()
