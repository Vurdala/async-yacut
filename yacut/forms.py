from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField, FileAllowed
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import (
    DataRequired, Length, Optional, Regexp
)

from settings import Config, MAX_URL_LENGTH, MAX_SHORT_LENGTH

ORIGINAL_LINK_LABEL = 'Введите ссылку'
SHORT_LABEL = 'Введите короткий идентификатор'
SUBMIT_BUTTON_LABEL = 'Сократить ссылку'

FILE_FIELD_LABEL = 'Файл для загрузки'
UPLOAD_BUTTON_LABEL = 'Загрузить'

DATA_REQUIRED_MESSAGE = 'Обязательное поле'
FILE_REQUIRED_MESSAGE = 'Требуется выбрать хотя бы один файл'
SHORT_ID_ERROR_MESSAGE = 'Можно использовать только буквы и цифры'
FILE_ALLOWED_MESSAGE = 'Разрешены только изображения: jpg, png, jpeg, gif'


class URLForm(FlaskForm):
    original_link = URLField(
        ORIGINAL_LINK_LABEL,
        validators=[
            DataRequired(message=DATA_REQUIRED_MESSAGE),
            Length(max=MAX_URL_LENGTH)
        ],
    )
    custom_id = StringField(
        SHORT_LABEL,
        validators=[
            Optional(),
            Length(max=MAX_SHORT_LENGTH),
            Regexp(
                Config.SHORT_PATTERN,
                message=SHORT_ID_ERROR_MESSAGE
            )
        ]
    )
    submit = SubmitField(SUBMIT_BUTTON_LABEL)


class FileForm(FlaskForm):
    files = MultipleFileField(
        FILE_FIELD_LABEL,
        validators=[
            DataRequired(message=FILE_REQUIRED_MESSAGE),
            FileAllowed(
                Config.ALLOWED_EXTENSIONS,
                message=FILE_ALLOWED_MESSAGE
            )
        ],
    )
    submit = SubmitField(UPLOAD_BUTTON_LABEL)
