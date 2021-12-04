from validation import ServiceForm
from wtforms import StringField
from wtforms.validators import DataRequired


class DetailGetForm(ServiceForm):
    title_id = StringField(
        label='title_id',
        validators=[
            DataRequired(message='The title id is required.'),
        ]
    )
