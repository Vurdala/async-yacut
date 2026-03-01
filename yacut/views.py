from flask import flash, redirect, render_template

from settings import Config, SHORT_LINK_VIEW_NAME

from . import app, db
from .error_handlers import ERROR_SHORT_EXISTS
from .forms import FileForm, URLForm
from .models import URLMap
from .yandexdisk import sync_process_uploaded_files


ERROR_UPLOAD_MESSAGE = 'Ошибка загрузки:'


@app.route("/", methods=["GET", "POST"])
def index():
    form = URLForm()
    if not form.validate_on_submit():
        return render_template("index.html", form=form)
    try:
        return render_template(
            "index.html",
            form=form,
            short_link=URLMap.create(
                original=form.original_link.data,
                short=form.custom_id.data,
            ).get_short_link(),
        )
    except (ValueError, RuntimeError) as e:
        flash(str(e))
        return render_template("index.html", form=form)


@app.route("/<short>", endpoint=SHORT_LINK_VIEW_NAME)
def redirect_view(short):
    return redirect(URLMap.get_or_404(short).original)


@app.route('/files', methods=['GET', 'POST'])
def files_view():
    form = FileForm()
    if not form.validate_on_submit():
        return render_template('files.html', form=form)
    try:
        yadisk_urls = sync_process_uploaded_files(form.files.data)
    except (ValueError, RuntimeError) as e:
        flash(f'{ERROR_UPLOAD_MESSAGE}{e}')
        return render_template('files.html', form=form)
    try:
        last_index = len(yadisk_urls) - 1
        results = [
            {
                'name': storage.filename,
                'link': URLMap.create(
                    original=url,
                    commit=index == last_index,
                ).get_short_link(),
            }
            for index, (storage, url) in enumerate(
                zip(form.files.data, yadisk_urls)
            )
        ]
    except (ValueError, RuntimeError) as e:
        flash(str(e))
        return render_template('files.html', form=form)
    return render_template('files.html', form=form, results=results)
