from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def create_creator_list(creators: dict, user_id):
    builder = InlineKeyboardBuilder()

    for creator_name, creator_id in creators.items():
        builder.add(InlineKeyboardButton(text=creator_name,
                                                    callback_data=f"get_creator_task {creator_id} {user_id}"))
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


def edit_task_kb(reply_markup: list[list[InlineKeyboardButton]]):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Завершить",
                                     callback_data=f"complete_task {reply_markup[0][0].callback_data.split()[-1]}"))
    for btns_layer in reply_markup:
        [builder.add(btn) for btn in btns_layer if btn.text != "Начать"]

    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


async def create_work_kb(task_id: int, task_status: str, urls: list, state: FSMContext):
    builder = InlineKeyboardBuilder()

    if task_status in ("2", "3"):
        btn_text, btn_clbk = ("Завершить", f"complete_task {task_id}") if task_status == "3" else (
        "Начать", f"start_task {task_id}")
        builder.add(InlineKeyboardButton(text=btn_text, callback_data=btn_clbk))

    if not urls[0]:
        file_urls = []
        for url in urls:
            if "file" in url:
                file_urls.append(url)
            elif "folder" in url:
                print("url for folder is ", url)
                builder.add(InlineKeyboardButton(text="Прикрепить", callback_data=f"upload_file {task_id}"))
                await state.update_data({f"{task_id}_folder": url})

        if file_urls:
            builder.add(InlineKeyboardButton(text=f"файлы ({len(file_urls)})",
                                                   callback_data=f"get_files {task_id}"))

            await state.update_data({f"{task_id}_files": file_urls})
    builder.adjust(2)

    return builder.as_markup(resize_keyboard=True)


def main_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Заказчики"))

    return builder.as_markup(resize_keyboard=True)


def cancel_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Назад"))

    return builder.as_markup(resize_keyboard=True)











