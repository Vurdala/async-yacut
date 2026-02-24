from aiohttp import FormData

UPLOAD_URL = "https://cloud-api.yandex.net/v1/disk/resources/upload"
DOWNLOAD_URL = "https://cloud-api.yandex.net/v1/disk/resources/download"


async def upload_file_to_disk(file, short_id, session):
    filename = file.filename
    path_on_disk = f"/uploads/{short_id}_{filename}"

    async with session.get(
        UPLOAD_URL,
        params={"path": path_on_disk, "overwrite": "true"}
    ) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()
        upload_url = data["href"]

    file.seek(0)
    file_data = file.read()

    form_data = FormData()
    form_data.add_field(
        'file',
        file_data,
        filename=filename,
        content_type=file.content_type
    )

    async with session.put(upload_url, data=form_data) as resp:
        if resp.status not in (201, 202):
            return None

    async with session.get(
        DOWNLOAD_URL,
        params={"path": path_on_disk}
    ) as resp:
        if resp.status != 200:
            return None
        data = await resp.json()
        return data["href"]
