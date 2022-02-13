from wtforms import Field
from wtforms.widgets import TextInput


class CommaSeparatedField(Field):
    widget = TextInput()

    def __init__(self, coerce=int, **kwargs):
        self._coerce = coerce

        super().__init__(**kwargs)

    def _value(self):
        if self.data:
            return ', '.join(self.data)

        return ''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [self._coerce(x.strip()) for x in valuelist[0].split(',')]
        else:
            try:
                self.data = self.default()
            except TypeError:
                self.data = self.default
