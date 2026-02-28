from flask import flash, redirect, render_template

from . import app, db
from .forms import FileForm, URLForm
from .models import URLMap
from .yandexdisk import sync_process_uploaded_files
from .error_handlers import ERROR_SHORT_EXISTS
from settings import Config


ERROR_UPLOAD_MESSAGE = 'Ошибка загрузки:'


@app.route("/", methods=["GET", "POST"])
def index():
    form = URLForm()
    if not form.validate_on_submit():
        return render_template("index.html", form=form)
    try:
        short = form.custom_id.data
        if short and short in Config.RESERVED_ENDPOINTS:
            raise ValueError(ERROR_SHORT_EXISTS)

        url_map = URLMap.create(
            original=form.original_link.data,
            short=short,
            validate=False,
        )
        return render_template(
            "index.html", form=form, short_link=url_map.get_short_link()
        )
    except ValueError as e:
        flash(str(e))
        return render_template("index.html", form=form)


@app.route("/<short>", endpoint=Config.SHORT_LINK_VIEW_NAME)
def redirect_view(short):
    return redirect(URLMap.get_or_404(short).original)


@app.route('/files', methods=['GET', 'POST'])
def files_view():
    form = FileForm()
    if form.validate_on_submit():
        try:
            yadisk_results = sync_process_uploaded_files(form.files.data)
            results = []
            for item in yadisk_results:
                url_map = URLMap.create(
                    original=item['url'],
                    commit=False,
                )
                results = results + [
                    {'name': item['name'], 'link': url_map.get_short_link()}
                ]
            if results:
                db.session.commit()
            return render_template('files.html', form=form, results=results)
        except Exception as e:
            flash('Ошибка загрузки: {0}'.format(e))
    return render_template('files.html', form=form)
