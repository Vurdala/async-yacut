import asyncio
from http import HTTPStatus
from io import BytesIO

import aiohttp
from werkzeug.datastructures import FileStorage

from settings import Config


ERROR_GET_UPLOAD_LINK = 'Ошибка получения ссылки для загрузки'
ERROR_UPLOAD_FILE = 'Ошибка загрузки файла на Яндекс.Диск'
ERROR_GET_DOWNLOAD_LINK = 'Ошибка получения публичной ссылки'


async def process_uploaded_files(file_data):
    async with aiohttp.ClientSession(
        headers=Config.YANDEX_DISK_HEADERS
    ) as session:
        results = []
        for item in file_data:
            if isinstance(item, FileStorage):
                storage, display_name = item, item.filename
            elif isinstance(item, tuple) and len(item) == 2:
                stream, name = item
                storage = (
                    FileStorage(stream=stream, filename=name)
                    if isinstance(stream, BytesIO)
                    else FileStorage(
                        stream=BytesIO(stream.read()), filename=name
                    )
                )
                display_name = name
            else:
                raise ValueError(
                    'Неподдерживаемый формат файла: {0}'.format(type(item))
                )

            filename = storage.filename or display_name
            path_on_disk = '{0}{1}'.format(
                Config.YANDEX_DISK_PATH_PREFIX, filename
            )

            async with session.get(
                Config.YANDEX_DISK_UPLOAD_URL,
                params={'path': path_on_disk, 'overwrite': 'true'},
            ) as resp:
                if resp.status != HTTPStatus.OK:
                    raise RuntimeError(
                        '{0}: {1}'.format(
                            ERROR_GET_UPLOAD_LINK, await resp.text()
                        )
                    )
                upload_url = (await resp.json())['href']

            storage.stream.seek(0)
            file_bytes = storage.stream.read()
            async with session.put(upload_url, data=file_bytes) as upload_resp:
                if upload_resp.status not in (
                    HTTPStatus.CREATED, HTTPStatus.OK
                ):
                    raise RuntimeError(
                        '{0}: {1}'.format(
                            ERROR_UPLOAD_FILE, await upload_resp.text()
                        )
                    )

            async with session.get(
                Config.YANDEX_DISK_DOWNLOAD_URL,
                params={'path': path_on_disk},
            ) as resp:
                if resp.status != HTTPStatus.OK:
                    raise RuntimeError(
                        '{0}: {1}'.format(
                            ERROR_GET_DOWNLOAD_LINK, await resp.text()
                        )
                    )
                download_link = (await resp.json()).get('href')

            results = results + [
                {'name': display_name, 'url': download_link}
            ]

    return results


def sync_process_uploaded_files(file_data):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(process_uploaded_files(file_data))
    finally:
        loop.close()
