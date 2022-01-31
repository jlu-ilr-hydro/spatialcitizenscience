import pytest
from spatialcitizenscience.configuration import Config
from spatialcitizenscience.view import form
import datetime

fields = [
    Config(name='f_str', type='str', notnull=True, description='A str test äö', value='bla'),
    Config(name='f_int', type='int', notnull=True, description='A int test äö', value='3'),
    Config(name='f_float', type='float', notnull=True, description='A float test äö', value='4.5'),
    Config(name='f_date', type='date', notnull=True, description='A date test äö', value=datetime.datetime.fromisoformat('2022-01-26')),
    Config(name='f_datetime', type='datetime', notnull=True, description='A datetime test äö', value=datetime.datetime.fromisoformat('2022-01-26 16:18:00')),
    Config(name='f_select', type='str', notnull=True, description='A select test äö', options=['a', 'b', 'c'], value='a')
]


@pytest.mark.parametrize('field', fields)
def test_field_creation(field):
    wtf_field = form.get_wtf_field(field)
    assert wtf_field


@pytest.mark.parametrize('field', fields)
def test_single_field_in_form(field):
    Form = form.create_form_type([field])
    f = Form(**{field.name: field.value})
    f.validate()
    assert not f.errors, f'{field.type}: failed to validate. {f.data}'


@pytest.mark.parametrize('field', fields)
def test_fail_validation_single_field(field):
    Form = form.create_form_type([field])
    f = Form()
    f.validate()
    assert f.errors, field.type + ': Found no validation error, although data is missing'


@pytest.mark.parametrize('field', fields[:-1])
def test_no_validation_single_field(field):
    field.notnull = False
    Form = form.create_form_type([field])
    f = Form()
    f.validate()
    assert not f.errors, field.type + ': got validation errors, although validation was off: ' + ' '.join(f.errors[field.name])


def test_all_fields_in_form():
    Form = form.create_form_type(fields)
    f = Form(**{field.name: field.value for field in fields})
    f.validate()
    assert not f.errors, f'failed to validate. {f.errors}'

