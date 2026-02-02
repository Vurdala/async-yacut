from random import randrange, random
from . import db
import string

from flask import abort, flash, redirect, render_template, url_for, request

from .models import URLMap
from .forms import URLForm, FileForm

def get_unique_short_id(length=6):
    chars = string.ascii_letters + string.digits  # A-Za-z0-9
    for _ in range(10):
        short_id = ''.join(random.choices(chars, k=length))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
    # Если не удалось за 10 попыток — увеличиваем длину
    return get_unique_short_id(length + 1)

@app.route('/')
def index_view():
    form = URLForm()
    if form.validate_on_submit():
        short = form.custom_id.data or get_unique_short_id()
        url_map = URLMap(original=form.original_link.data, short=short)
        db.session.add(url_map)
        db.session.commit()
        flash(f'Ваша короткая ссылка: {request.host_url}{short}')
        return render_template('index.html', form=form, short=short)
    return render_template('index.html', form=form)


@app.route('/files')
def files_view():
