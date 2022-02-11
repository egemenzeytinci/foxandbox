from validation import ServiceForm
from validation.custom import CommaSeparatedField
from wtforms import DecimalField, IntegerField, StringField
from wtforms.validators import DataRequired, Optional, NumberRange


class MovieListForm(ServiceForm):
    genres = CommaSeparatedField(
        StringField(
            'genres',
            validators=[Optional()]
        ),
        default=['Drama']
    )

    years = CommaSeparatedField(
        IntegerField(
            'years',
            validators=[Optional()]
        ),
        default=['1979, 1989, 1999, 2009']
    )

    score = DecimalField(
        label='score',
        validators=[
            Optional(),
            NumberRange(min=5.0, max=9.0, message='The score must be between 5.0 and 9.0.')
        ],
        default=8.0
    )

    num_votes = IntegerField(
        label='num_votes',
        validators=[
            Optional(),
            NumberRange(
                min=5000,
                max=25000,
                message='The number of votes must be between 5000 and 25000.'
            )
        ],
        default=25000
    )

    page = IntegerField(
        label='page',
        validators=[
            DataRequired('The page number is required.'),
            NumberRange(min=1, message='The page number must be at least 1.')
        ]
    )
