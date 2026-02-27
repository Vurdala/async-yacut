from flask import flash, redirect, render_template

from . import app
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
        url_map = URLMap.create(
            original=form.original_link.data,
            short=form.custom_id.data
        )
        return render_template(
            "index.html", form=form, short_link=url_map.get_short_link()
        )
    except ValueError as e:
        flash(str(e))
        return render_template("index.html", form=form)


@app.route("/<short>")
def redirect_view(short):
    return redirect(URLMap.get_or_404(short).original)


@app.route('/files', methods=['GET', 'POST'])
def files_view():
    form = FileForm()
    if form.validate_on_submit():
        try:
            results = sync_process_uploaded_files(form.files.data)
            return render_template('files.html', form=form, results=results)
        except Exception as e:
            flash(f'Ошибка загрузки: {e}')
    return render_template('files.html', form=form)
