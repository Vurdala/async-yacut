import asyncio
from http import HTTPStatus
from io import BytesIO

import aiohttp
from werkzeug.datastructures import FileStorage

from settings import (
    Config,
    YANDEX_DISK_DOWNLOAD_URL,
    YANDEX_DISK_HEADERS,
    YANDEX_DISK_UPLOAD_URL,
)


ERROR_GET_UPLOAD_LINK = 'Ошибка получения ссылки для загрузки'
ERROR_UPLOAD_FILE = 'Ошибка загрузки файла на Яндекс.Диск'
ERROR_GET_DOWNLOAD_LINK = 'Ошибка получения публичной ссылки'


async def _upload_file_and_get_url(session, storage: FileStorage) -> str:
    path_on_disk = f'{Config.YANDEX_DISK_PATH_PREFIX}{storage.filename}'

    async with session.get(
        YANDEX_DISK_UPLOAD_URL,
        params={'path': path_on_disk, 'overwrite': 'true'},
    ) as resp:
        if resp.status != HTTPStatus.OK:
            raise RuntimeError(
                f'{ERROR_GET_UPLOAD_LINK}: {await resp.text()}'
            )
        upload_url = (await resp.json())['href']

    storage.stream.seek(0)
    async with session.put(
        upload_url,
        data=storage.stream.read(),
    ) as upload_resp:
        if upload_resp.status not in (HTTPStatus.CREATED, HTTPStatus.OK):
            raise RuntimeError(
                f'{ERROR_UPLOAD_FILE}: {await upload_resp.text()}'
            )

    async with session.get(
        YANDEX_DISK_DOWNLOAD_URL,
        params={'path': path_on_disk},
    ) as resp:
        if resp.status != HTTPStatus.OK:
            raise RuntimeError(
                f'{ERROR_GET_DOWNLOAD_LINK}: {await resp.text()}'
            )
        return (await resp.json()).get('href')


async def process_uploaded_files(file_data):
    async with aiohttp.ClientSession(
        headers=YANDEX_DISK_HEADERS
    ) as session:
        urls = []
        for item in file_data:
            urls.append(await _upload_file_and_get_url(session, item))

    return urls


def sync_process_uploaded_files(file_data):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(process_uploaded_files(file_data))
    finally:
        loop.close()
