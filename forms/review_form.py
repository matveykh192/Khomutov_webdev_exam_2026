from flask_wtf import FlaskForm

from wtforms import (
    SelectField,
    TextAreaField,
    SubmitField
)

from wtforms.validators import (
    DataRequired
)


class ReviewForm(FlaskForm):

    rating = SelectField(
        "Оценка",
        choices=[
            (5, "Отлично"),
            (4, "Хорошо"),
            (3, "Удовлетворительно"),
            (2, "Неудовлетворительно"),
            (1, "Плохо"),
            (0, "Ужасно")
        ],
        coerce=int
    )

    text = TextAreaField(
        "Текст рецензии",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField(
        "Сохранить"
    )