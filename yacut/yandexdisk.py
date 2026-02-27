import asyncio
from http import HTTPStatus
from io import BytesIO

import aiohttp
from werkzeug.datastructures import FileStorage

from settings import (
    Config, YANDEX_DISK_UPLOAD_URL,
    YANDEX_DISK_DOWNLOAD_URL
)

from .models import URLMap


ERROR_GET_UPLOAD_LINK = 'Ошибка получения ссылки для загрузки'
ERROR_UPLOAD_FILE = 'Ошибка загрузки файла на Яндекс.Диск'
ERROR_GET_DOWNLOAD_LINK = 'Ошибка получения публичной ссылки'


async def process_uploaded_files(file_data):
    def _normalize_item(item):
        if isinstance(item, FileStorage):
            return item, item.filename
        if isinstance(item, tuple) and len(item) == 2:
            stream, name = item
            if isinstance(stream, BytesIO):
                fs = FileStorage(stream=stream, filename=name)
            else:
                fs = FileStorage(stream=BytesIO(stream.read()), filename=name)
            return fs, name
        raise ValueError(f'Неподдерживаемый формат файла: {type(item)}')

    files = [_normalize_item(item) for item in file_data]

    async with aiohttp.ClientSession(
        headers=Config.YANDEX_DISK_HEADERS
    ) as session:
        results = []
        for storage, display_name in files:
            filename = storage.filename or display_name
            path_on_disk = f"{Config.YANDEX_DISK_PATH_PREFIX}{filename}"

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
            file_bytes = storage.stream.read()
            async with session.put(upload_url, data=file_bytes) as upload_resp:
                if upload_resp.status not in (
                    HTTPStatus.CREATED, HTTPStatus.OK
                ):
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
                download_link = (await resp.json()).get('href')

            url_map = URLMap.create(original=download_link)
            short_link = f'http://localhost/{url_map.short}'

            results = results + [
                {
                    'name': display_name,
                    'link': short_link,
                }
            ]

    return [item for item in results]


def sync_process_uploaded_files(file_data):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(process_uploaded_files(file_data))
    finally:
        loop.close()
