import aiohttp

from http import HTTPStatus
from settings import Config

from .models import URLMap


async def upload_file_to_disk(files, token):
    headers = {}
    if token:
        headers["Authorization"] = f"OAuth {token}"

    results = []

    async with aiohttp.ClientSession(headers=headers) as session:
        for storage, display_name in files:
            filename = storage.filename or display_name
            path_on_disk = f"{Config.YANDEX_DISK_PATH_PREFIX}{filename}"

            async with session.get(
                Config.YANDEX_DISK_UPLOAD_URL,
                params={"path": path_on_disk, "overwrite": "true"},
            ) as resp:
                if resp.status != HTTPStatus.OK:
                    text = await resp.text()
                    raise RuntimeError(f"Ошибка получения ссылки: {text}")
                upload_url = (await resp.json())["href"]

            storage.stream.seek(0)
            file_bytes = storage.stream.read()
            form_data = aiohttp.FormData()
            form_data.add_field(
                "file",
                file_bytes,
                filename=filename,
                content_type=getattr(storage, "content_type", None),
            )

            async with session.put(upload_url, data=form_data) as resp:
                if resp.status not in (
                    HTTPStatus.CREATED,
                    HTTPStatus.ACCEPTED,
                    HTTPStatus.NO_CONTENT,
                ):
                    text = await resp.text()
                    raise RuntimeError(f"Ошибка загрузки файла: {text}")

            async with session.get(
                Config.YANDEX_DISK_DOWNLOAD_URL,
                params={"path": path_on_disk},
            ) as resp:
                if resp.status != HTTPStatus.OK:
                    text = await resp.text()
                    raise RuntimeError(
                        f"Ошибка получения публичной ссылки: {text}"
                    )
                download_link = (await resp.json()).get("href")

            url_map = URLMap.create(original=download_link)
            short_link = f"{Config.BASE_URL}/{url_map.short}"

            results.append({"name": display_name, "link": short_link})

    return results
