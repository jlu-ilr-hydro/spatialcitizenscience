
from flask_wtf import FlaskForm
import wtforms as wtf
import datetime


def datetime_field_factory(*args, **kwargs):
    """
    A factory to create a DateTimeLocalField with "now" as the default value
    and the correct format
    """
    kwargs.setdefault('default', datetime.datetime.now)
    kwargs.setdefault('format', '%Y-%m-%dT%H:%M')
    return wtf.DateTimeLocalField(*args, **kwargs)


_field_types = dict(
    int=wtf.IntegerField,
    float=wtf.FloatField,
    str=wtf.StringField,
    bool=wtf.BooleanField,
    date=wtf.DateField,
    datetime=datetime_field_factory,
)


def get_wtf_field(field):
    """
    Create a WTForms field from a configuration of a field
    """
    if 'notnull' in field and field.notnull:
        validators = [wtf.validators.DataRequired()]
    else:
        validators = [wtf.validators.Optional()]
    if 'options' in field:
        return wtf.SelectField(field.description, choices=field.options, validators=validators)

    return _field_types[field.type](field.description, validators=validators)


def create_form_type(fields, use_flask_wtf=False):
    """
    Create a WTFForms form class, either inheriting from `WTForms.Form` or from `flask_wtf.FlaskForm`
    :param fields: List of
    :param use_flask_wtf: If True, use `flask_wtf.FlaskForm` as base class, else inherit from `WTForms.Form`
    :return: class SpCiSciFrom

    Usage:
    >>>Form = create_from_type(config.database.fields)
    >>>form = Form()
    """
    Form = FlaskForm if use_flask_wtf else wtf.Form
    return type(
        'SpCiSciForm', (Form, ),
        {
            field.name: get_wtf_field(field)
            for field in fields
        }
    )

