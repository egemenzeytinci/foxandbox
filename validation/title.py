from validation import ServiceForm
from validation.custom import CommaSeparatedField
from wtforms import BooleanField, DecimalField, IntegerField, StringField
from wtforms.validators import AnyOf, DataRequired, InputRequired, Optional, NumberRange


class TitleListForm(ServiceForm):
    genres = CommaSeparatedField(
        validators=[Optional()],
        coerce=str,
        default='Drama, Comedy, Romance'
    )

    years = CommaSeparatedField(
        validators=[Optional()],
        coerce=int,
        default='1979, 1989, 1999, 2009, 2019'
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

    exact = BooleanField(
        label='exact',
        validators=[
            InputRequired('The exact match selection is required.'),
        ],
        false_values=('false', 'False', '')
    )

    type = StringField(
        'type',
        validators=[
            DataRequired('The type is required.'),
            AnyOf(values=['movie', 'series'])
        ]
    )

    page = IntegerField(
        label='page',
        validators=[
            DataRequired('The page number is required.'),
            NumberRange(min=1, message='The page number must be at least 1.')
        ]
    )
