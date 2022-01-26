from flask_wtf import FlaskForm
import wtforms as wtf

from .configuration import Config



def get_field_type(field: Config):
    if 'options' in field:
        return wtf.SelectField(field.description, choices=field.options)
    field_types = dict(
        int=wtf.IntegerField,
        float=wtf.FloatField,
        str=wtf.StringField,
        bool=wtf.BooleanField
    )

    return field_types[]
def create_form_type(config: Config):
    ...