import base64
import re
from os import getenv


def get_name_by_group(group_name: str) -> str:
    match = re.search(r'Клиент\s+([^:]+?)\s+(?=Сделка)', group_name)

    result = match.group(1) if not match else "Неизвестно"

    if len(result.split(" ")) > 1:
        full_name = result.split(" ")

        second_name = full_name[0][0]
        last_name = full_name[-1]

        return f"{last_name} {second_name}."
    return result


async def encode_file_to_base64(file_buffer: memoryview) -> str:
    encoded_content = base64.b64encode(file_buffer)

    return encoded_content.decode("utf-8")
