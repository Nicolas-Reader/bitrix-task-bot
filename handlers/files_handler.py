import logging
from io import BytesIO

from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile, Message
from aiogram.fsm.context import FSMContext

from bitrix_manager.bitrix24_manager import AsyncBitrixManager
from kbs.keyboards_user import cancel_kb, main_kb
from utils.utils import delete_all_task, create_all_task
from states import EnterPhoto


async_bx = AsyncBitrixManager()

router = Router()


@router.callback_query(F.data.startswith("upload_file"))
async def upload_file_cbk(callback: CallbackQuery, state: FSMContext) -> None:
    task_id = callback.data.split(" ")[1]
    folder_url = await state.get_value(f"{task_id}_folder")

    await state.update_data(current_task_id=task_id, current_url=folder_url)
    message_ids = await state.get_value("message_ids")
    await delete_all_task(callback.message, message_ids, callback.message.message_id)
    await callback.message.answer("Отправьте файлы для прикрепления", reply_markup=cancel_kb())
    # На заказы связзанными с данной темой нельзя отправлять файлы
    for keyword in ["бытовк", "комплекту", "туалет"]:
        if keyword not in callback.message.text.lower():
            return
    await callback.message.answer("⚠️ПРЕДУПРЕЖДЕНИЕ: для удачного завершения заказа необходимо загрузить минимум 10 фото⚠️")

    await state.set_state(EnterPhoto.attach_files)


@router.callback_query(F.data.startswith("get_files"))
async def get_files_cbk(callback: CallbackQuery, state: FSMContext) -> None:
    task_id = callback.data.split(" ")[1]
    file_urls = await state.get_value(f"{task_id}_files")
    group = await state.get_value(f"{task_id}_group")

    for file_url in file_urls:
        file = await async_bx.disk_file_get(file_url, group)
        await callback.message.answer_document(BufferedInputFile(file.getbuffer(), file.name))


@router.message(EnterPhoto.attach_files, F.content_type.in_(['photo', 'document']))
async def attach_file(message: Message, state: FSMContext) -> None:
    file_content = BytesIO()

    if message.content_type == 'photo':
        await message.bot.download(file=message.photo[-1].file_id, destination=file_content)
        file_info = await message.bot.get_file(message.photo[-1].file_id)
        file_name = file_info.file_path.split('/')[-1]
    else:
        await message.bot.download(file=message.document.file_id, destination=file_content)
        file_name = message.document.file_name

    file_content.seek(0)

    url = await state.get_value("current_url")
    task_id = await state.get_value("current_task_id")
    group_name = await state.get_value(f"{task_id}_group")

    folder_id = await async_bx.get_folder_id(url, group_name)
    msg = await message.answer("Отправляется на сервер")
    try:
        await async_bx.attach_file(folder_id, file_name, file_content.getbuffer())
    except Exception as e:
        logging.error(e, "Exception while loading file on server")

        await msg.edit_text("Произошла ошибка при загрузке на сервер")
        return
    await msg.edit_text("Отправка прошла успешно")


@router.message(EnterPhoto.attach_files)
async def attach_text(message: Message) -> None:
    await message.answer("Нельзя отправлять текст на сервер, выйти из прикрепления можно через кнопку")


@router.message(EnterPhoto.attach_files, F.text == "Назад")
async def cancel_files_handler(message: Message, state: FSMContext) -> None:
    await message.answer("Отправка файлов в заказ прекращена", reply_markup=main_kb())

    await state.set_state(state=None)
    await create_all_task(message, state)
