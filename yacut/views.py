from . import db

import asyncio
from flask import flash, render_template, request, redirect
import aiohttp

from . import app
from .models import URLMap
from .forms import URLForm, FileForm
from .utils import get_unique_short_id
from .yandexdisk import upload_file_to_disk

RESERVED_ENDPOINTS = {'files', 'index', 'static'}


@app.route("/", methods=["GET", "POST"])
def index_view():
    form = URLForm()
    short_link = None

    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = form.custom_id.data or get_unique_short_id()

        if custom_id in {'files'}:
            flash('Предложенный вариант короткой ссылки уже существует.')
            return render_template('index.html', form=form)

        if URLMap.query.filter_by(short=custom_id).first():
            flash('Предложенный вариант короткой ссылки уже существует.')
            return render_template('index.html', form=form)

        url_map = URLMap(original=original, short=custom_id)
        db.session.add(url_map)
        db.session.commit()

        short_link = f'{request.host_url}{custom_id}'
        flash(f'Ваша короткая ссылка: {short_link}')

    return render_template('index.html', form=form, short_link=short_link)


@app.route('/<short_id>')
def redirect_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)


@app.route("/files", methods=["GET", "POST"])
def files_view():
    form = FileForm()
    results = []

    if form.validate_on_submit():
        uploaded_files = form.files.data
        successful_uploads = []

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run_uploads():
            async with aiohttp.ClientSession(
                headers={"Authorization": app.config["DISK_TOKEN"]}
            ) as session:
                for file in uploaded_files:
                    if file and file.filename:
                        short_id = get_unique_short_id()
                        url_map = URLMap(
                            original=f"https://disk.yandex.ru/d/{short_id}",
                            short=short_id,
                        )
                        db.session.add(url_map)
                        db.session.commit()

                        _ = await upload_file_to_disk(
                            file, short_id, session
                        )
                        link = f"{request.host_url}{short_id}"
                        successful_uploads.append(
                            {"name": file.filename, "link": link}
                        )
                return successful_uploads

        try:
            uploads = loop.run_until_complete(run_uploads())
            results.extend(uploads)
        except Exception as e:
            flash(f"Ошибка: {e}")

    return render_template("files.html", form=form, results=results)
