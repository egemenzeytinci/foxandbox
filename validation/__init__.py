from datetime import datetime, date, time
from flask_wtf import FlaskForm
from werkzeug.datastructures import MultiDict
from wtforms import FieldList


class BaseForm(FlaskForm):
    def pre_format(self, field):
        """
        Format fields for validation

        :param wtforms.fields.core.Field field: form field
        :return: formatted field value
        :rtype: str
        """
        # get type of the value
        t = type(field.data)

        # format value according to type
        if t is datetime:
            return field.data.strftime(field.format)
        if t is date:
            return field.data.strftime(field.format)
        if t is time:
            return field.data.strftime(field.format)
        if t is bool:
            return 'true' if field.data else 'false'

        return str(field.data)

    def validate(self, extra_validators=None):
        """
        Validate form

        :param list[str] extra_validators: field names to lists of extra validator
        :return: true if form valid, false otherwise
        :rtype: bool
        """
        for k in self._fields:
            f = self._fields.get(k)

            # check if value is empty
            if f.data is None:
                continue

            # check if form field is already processed
            if f.raw_data is not None and len(f.raw_data) > 0:
                continue

            m = MultiDict()

            if type(f) == FieldList:
                # iterate through unbound field of field list
                for i, _ in enumerate(f.data):
                    f.unbound_field.data = f.data[i]

                    m.add(f'{k}-{i}', self.pre_format(f.unbound_field))
            else:
                m.add(k, self.pre_format(f))

            # process unbound form field
            self._fields.get(k).process(m)

        return super(BaseForm, self).validate(extra_validators)

    def error(self):
        """
        Get first form error

        :return: error message
        :rtype: str or None
        """
        if len(self.errors) == 0:
            return None

        for e in self.errors:
            for err in self.errors[e]:
                if len(err) == 0:
                    continue

                if type(err) == list:
                    return err[0]
                return err

        return None

    def error_group(self):
        """
        Get form errors

        :return: list of errors
        :rtype: list[str]
        """
        if len(self.errors) == 0:
            return []

        errors = []
        for es in self.errors:
            for e in self.errors[es]:
                if type(e) == list:
                    errors.append(e[0])
                else:
                    errors.append(e)

        return errors


class ServiceForm(BaseForm):
    class Meta:
        csrf = False
