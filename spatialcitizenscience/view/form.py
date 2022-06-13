
from flask_wtf import FlaskForm
import wtforms as wtf
import datetime
from ..configuration import Config
from string import ascii_uppercase, digits
import random

def datetime_field_factory(*args, **kwargs):
    """
    A factory to create a DateTimeLocalField with "now" as the default value
    and the correct format
    """
    kwargs.setdefault('default', datetime.datetime.now)
    kwargs.setdefault('format', ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M"])
    return wtf.DateTimeLocalField(*args, **kwargs)


_field_types = dict(
    int=wtf.IntegerField,
    float=wtf.FloatField,
    str=wtf.StringField,
    bool=wtf.BooleanField,
    date=wtf.DateField,
    datetime=datetime_field_factory,
)


def get_wtf_field(field: Config) -> wtf.Field:
    """
    Create a WTForms field from a configuration of a field
    """
    render_kw = {}
    label = field.get('description', field.name)
    FType = _field_types[field.type]

    if 'notnull' in field and field.notnull:
        validators = [wtf.validators.DataRequired()]
    else:
        validators = [wtf.validators.Optional()]
    if field.get('readonly'):
        render_kw['disabled'] = 'disabled'
    if 'default' in field:
        if field.type.startswith('date') and  field['default'] == 'now':
            value = datetime.datetime.now()
        else:
            value = field['default']
    elif 'random' in field:
        if field.type == 'int':
            value = random.randint(0, 10 ** field.random)
        elif field.type == 'str':
            value = ''.join(random.choices(ascii_uppercase + digits, k=field.random))
        elif field.type == 'float':
            value = random.random() * 10 ** field.random
        else:
            raise ValueError('Only int, str, and float fields can have a random default')

    else:
        value = None

    if 'options' in field:
        return wtf.SelectField(field.description, choices=field.options, validators=validators, default=value)
    else:
        return FType(label, validators=validators, default=value, render_kw=render_kw)


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

