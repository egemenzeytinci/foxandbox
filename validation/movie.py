from validation import ServiceForm
from validation.custom import CommaSeparatedField
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired, NumberRange


class MovieListForm(ServiceForm):
    genres = CommaSeparatedField(
        StringField(
            'genres',
            validators=[
                DataRequired(message='The genres field is required.')
            ]
        )
    )

    years = CommaSeparatedField(
        StringField(
            'years',
            validators=[
                DataRequired(message='The years field is required.')
            ]
        )
    )

    page = IntegerField(
        label='page',
        validators=[
            DataRequired(),
            NumberRange(min=1, message='The page number must be at least 1.')
        ]
    )
