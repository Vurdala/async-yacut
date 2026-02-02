from random import randrange

from flask import abort, flash, redirect, render_template, url_for

from . import app, db
from .forms import URLForm, FileForm
from .models import URLMap


def get_unique_short_id():
    for _ in range(10):
        short_id = hex(randrange(16**16))[2:]
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
    else:
        abort(500)
