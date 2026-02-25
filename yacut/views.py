from flask import flash, redirect, render_template, request, url_for
from werkzeug.datastructures import FileStorage

import asyncio

from . import app
from .forms import FileForm, URLForm
from .models import URLMap
from .yandexdisk import upload_file_to_disk
from .error_handlers import InvalidAPIUsage


@app.route("/", methods=["GET", "POST"])
def index():
    form = URLForm()
    if form.validate_on_submit():
        original = form.original_link.data
        custom_id = form.custom_id.data or None

        try:
            url_map = URLMap.create(original=original, short=custom_id)
            short_link = url_for(
                "redirect_view", short=url_map.short, _external=True
            )
            return render_template("index.html", form=form, short_link=short_link)
        except InvalidAPIUsage as e:
            flash(e.message)

    return render_template("index.html", form=form)


@app.route("/<short>")
def redirect_view(short):
    url_map = URLMap.get_or_404(short)
    return redirect(url_map.original)


@app.route("/files", methods=["GET", "POST"])
def files_view():
    form = FileForm()
    if form.validate_on_submit():
        try:
            files = []
            file_objects = form.files.data or request.files.getlist("files")

            for f in file_objects:
                if isinstance(f, FileStorage):
                    files.append((f, f.filename))
                else:
                    stream, name = f
                    fs = FileStorage(stream=stream, filename=name)
                    files.append((fs, name))

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(
                upload_file_to_disk(files, app.config["DISK_TOKEN"])
            )
            return render_template("files.html", form=form, results=results)
        except Exception as e:
            flash(f"Ошибка загрузки: {e}")
    return render_template("files.html", form=form)

