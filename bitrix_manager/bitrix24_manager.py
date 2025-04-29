import asyncio

from os import getenv
from io import BytesIO
from typing import Literal

import requests

from fast_bitrix24 import BitrixAsync
from dotenv import load_dotenv

from utils.biitrix_utils import get_name_by_group, encode_file_to_base64


load_dotenv(".env")


class AsyncBitrixManager:
    def __init__(self) -> None:
        webhook = getenv("B24_WEBHOOK")

        self.__async_bx = BitrixAsync(webhook)

    async def get_tasks(self, user_id: int) -> list:
        return await self.__async_bx.get_all('tasks.task.list', {"filter": {"RESPONSIBLE_ID": user_id}})

    async def get_tasks_by_creator(self, user_id: int, creator_id) -> list:
        return await self.__async_bx.get_all('tasks.task.list',
                                                   {"filter": {"RESPONSIBLE_ID": user_id, "CREATED_BY": creator_id}})

    async def get_task_by_group(self, user_id: int, group_id: int) -> list:
        return await self.__async_bx.get_all('tasks.task.list',
                                                   {"filter": {"RESPONSIBLE_ID": user_id, "GROUP_ID": group_id}})

    async def get_task_creators(self, user_id: int) -> dict:
        creators_info = dict()

        user_tasks = await self.get_tasks(user_id)

        for user_task in user_tasks:
            if int(user_task.get("status")) > 3:
                continue

            creator_info = dict(user_task).get("creator")

            if creator_info:
                name = creator_info.get("name").split()

                first_name = name[0]
                short_second_name = name[-1][0] + "."

                creator_id = creator_info.get("id")

                creators_info[f'{first_name} {short_second_name}'] = creator_id

        return creators_info

#   >---------< ARCHIVED >-----------<
    async def get_task_customer(self, user_id: int) -> dict:
        customers_info = dict()

        user_tasks = await self.get_tasks(user_id)

        for user_task in user_tasks:
            if int(user_task.get("status")) > 3:
                continue

            user_task: dict = dict(user_task)

            if user_task.get("group"):
                group: dict = user_task["group"]

                group_id = group["id"]
                group_name = group["name"]

                name = get_name_by_group(group_name)

                customers_info[name] = group_id

        return customers_info

    async def interact_task(self, task_id: int, action: Literal["start", 'pause', 'complete']):
        return await self.__async_bx.call(f"tasks.task.{action}", {"taskId": task_id})

    async def attach_file(self, folder_id: int, file_name: str, file_buffer):
        base64_file_content = await encode_file_to_base64(file_buffer)

        return await self.__async_bx.call("disk.folder.uploadfile",
          {
              "id": int(folder_id),
              "data": {"NAME": file_name,},
              "fileContent": base64_file_content,
          })

    async def disk_file_get(self, url: str, group_name) -> BytesIO:
        main_folder_id = (await self.__async_bx.call('disk.storage.getlist', {"filter": {"NAME": group_name}}))["ID"]

        path = url.split("/disk/file/")[1].split("/")

        replace_func = lambda x: x.replace("%20", " ").replace("%23", "#")
        full_path = list(map(replace_func, path))

        next_id = (await self.__async_bx.call('disk.storage.getchildren', {"id": int(main_folder_id),
                                                                          "filter": {"NAME": full_path[0]}}))["ID"]

        for folder_name in full_path[1:]:
            next_id = (await self.__async_bx.call('disk.folder.getchildren', {"id": int(next_id),
                                                          "filter": {"NAME": folder_name}}))["ID"]

        download_link = await self.__async_bx.call('disk.file.get', {"id": int(next_id)})
        resp = requests.get(list(dict(download_link).values())[0]["DOWNLOAD_URL"])

        file = BytesIO(resp.content)
        file.seek(0)

        file.name = full_path[-1]

        return file

    async def get_folder_id(self, url, group_name):
        main_folder_id = (await self.__async_bx.get_all('disk.storage.getlist',
                                                       {"filter": {"NAME": group_name[:100]}}))[0]["ID"]

        split_path = url.split("/disk/path/")[1].split("/")
        replace_func = lambda x: x.replace("%20", " ").replace("%23", "#")

        full_path = list(map(replace_func, split_path))

        next_id = (await self.__async_bx.call('disk.storage.getchildren', {"id": int(main_folder_id),
                                                       "filter": {"NAME": full_path[0]}}))["ID"]

        for folder_name in full_path[1:-1 if url.endswith("/") else None]:
            next_id = (await self.__async_bx.call('disk.folder.getchildren', {"id": int(next_id),
                                                          "filter": {"NAME": folder_name}}))["ID"]

        return next_id


async def main():
    as_bx = AsyncBitrixManager()
    id = await as_bx.get_folder_id("https://ideisruba.bitrix24.ru/workgroups/group/597/disk/path/folder_16735/Фотоотчёты%20по%20сделке%20_Дикаприо%20%20%2316735%20_/Фотоотчёт%20завоз%20Тулета/", 'Клиент Дикаприо  Сделка Дикаприо  #16735  Проект Прая')

if __name__ == '__main__':
    asyncio.run(main())