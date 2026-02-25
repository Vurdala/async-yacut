from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField, FileAllowed
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import (
    DataRequired, Length, Optional, Regexp
)

from settings import Config

ORIGINAL_LINK_LABEL = 'Введите ссылку'
CUSTOM_ID_LABEL = 'Введите короткий идентификатор'
SUBMIT_BUTTON_LABEL = 'Сократить ссылку'

FILE_FIELD_LABEL = 'Файл для загрузки'
UPLOAD_BUTTON_LABEL = 'Загрузить'


class URLForm(FlaskForm):
    original_link = URLField(
        ORIGINAL_LINK_LABEL,
        validators=[
            DataRequired(message='Обязательное поле'),
            Length(max=Config.MAX_URL_LENGTH)
        ],
    )
    custom_id = StringField(
        CUSTOM_ID_LABEL,
        validators=[
            Optional(),
            Length(max=Config.MAX_SHORT_ID_LENGTH),
            Regexp(
                r'^[a-zA-Z0-9]*$',
                message='Можно использовать только буквы и цифры'
            )
        ]
    )
    submit = SubmitField(SUBMIT_BUTTON_LABEL)


class FileForm(FlaskForm):
    files = MultipleFileField(
        FILE_FIELD_LABEL,
        validators=[
            DataRequired(message='Требуется выбрать хотя бы один файл'),
            FileAllowed(
                Config.ALLOWED_EXTENSIONS,
                message='Разрешены только изображения'
            )
        ],
    )
    submit = SubmitField(UPLOAD_BUTTON_LABEL)