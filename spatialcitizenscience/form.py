from flask_wtf import FlaskForm
import wtforms as wtf


_field_types = dict(
    int=wtf.IntegerField,
    float=wtf.FloatField,
    str=wtf.StringField,
    bool=wtf.BooleanField,
    date=wtf.DateField,
    datetime=wtf.DateTimeLocalField,
)


def get_wtf_field(field):

    if 'notnull' in field and field.notnull:
        validators = [wtf.validators.DataRequired()]
    else:
        validators = []
    if 'options' in field:
        return wtf.SelectField(field.description, choices=field.options, validators=validators)

    return _field_types[field.type](field.description, validators=validators)


def create_form_type(fields, use_flask_wtf=False):
    Form = FlaskForm if use_flask_wtf else wtf.Form
    return type(
        'SpCiSciForm', (Form, ),
        {
            field.name: get_wtf_field(field)
            for field in fields
        }
    )

