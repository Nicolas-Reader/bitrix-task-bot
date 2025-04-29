import urllib.parse
import re

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import html

from bitrix_manager.bitrix24_manager import AsyncBitrixManager
from kbs.keyboards_user import create_work_kb


async_bx = AsyncBitrixManager()


def get_formated_links(text: str) -> tuple[list[list[str]], list[str]]:
    result = re.findall(r"\[URL=([^\]]+?)\]([^\[]*?)\[\/URL\]", text)
    replace_links = re.findall(r"\[URL=[^\]]+?\][^\[]*?\[\/URL\]", text)

    links, links_original = [], []

    for link_info, replace_link in zip(result, replace_links):
        unquote_link = urllib.parse.unquote(link_info[0])
        link_text = link_info[1]

        links_original.append(unquote_link)
        link = {"url": unquote_link, "name": link_text}

        links.append([link, replace_link])
    return links, links_original


def get_links(text: str) -> list[str]:
    result = re.findall(r"www|http:|https:+\S+\w", text)

    links = []
    for link in result:
        if any(char in link for char in ["URL", "[", "]", "path"]):
            continue

        links.append(urllib.parse.unquote(link))

    return links



async def send_tasks(tasks: list[dict], msg: Message, state: FSMContext) -> None:
    task_ids = []
    for task in tasks:
        task_id = task.get("id")
        task_status = task.get("status")

        if int(task_status) > 3:
            continue

        task_message, links_original = (await get_task_message(task, state)).values
        reply_kb = await create_work_kb(task_id, task_status, links_original, state)
        msg = await msg.answer(task_message, reply_markup=reply_kb)
        task_ids.append(msg.message_id)

    await state.update_data(message_ids=task_ids)


async def delete_all_task(msg: Message, msg_ids: list, not_deleted_id: int) -> None:
    # удаляем все присланные ранее задачи, кроме выбранной
    [await msg.bot.delete_message(msg.chat.id, msg_id) for msg_id in msg_ids if msg_id != not_deleted_id]


async def create_all_task(msg: Message, state: FSMContext) -> None:
    user_id, creator_id = await state.get_value('button_info')
    tasks = await async_bx.get_tasks_by_creator(user_id, creator_id)

    await state.update_data(task_count=len(tasks))

    await send_tasks(tasks, msg, state)


async def get_task_message(task: dict, state: FSMContext) -> dict[str, str | list[str]]:
    status_preset = {0: "Отсутсвует", 2: 'Ждет выполнения',
                     3: 'Выполняется', 4: 'Ожидает контроля',
                     5: 'Завершена', 6: 'Отложена'}

    none_mess = "Нет информации"

    task_name = task.get('title', __default=none_mess)
    task_description = task.get('description', __default=none_mess)
    task_id = task.get('id')
    task_status = status_preset[int(task.get("status")) or 0]

    urls, links_original = get_formated_links(task_description)
    bold = lambda text: html.bold(text)

    await state.update_data(
        {f"{task_id}_group": task["group"]["name"]}
        if task["group"] else None
    )

    links = get_links(task_description)

    for link in links:
        task_description = task_description.replace(link, html.link("ссылка", link))
    for url in urls:
        link, replace_link = url

        task_description = task_description.replace(replace_link, html.link(link['name'], link['url']))

    return {"message_text": (f"{bold('Статус')}:\n{task_status}\n" +
                             f"{bold('Название')}:\n{task_name}\n" +
                             f"{bold('Описание')}:\n{task_description}\n"),
            "links": links_original + [link for link in links if link not in links_original]}
