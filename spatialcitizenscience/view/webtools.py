import flask
import bleach
import markdown


def clean(text: str):
    """
    Cleans user given text using the
    :param text:
    :return:
    """
    return flask.Markup(
        bleach.clean(
            text,
            bleach.ALLOWED_TAGS + ['sub', 'sup'],
            ['class']
        )
    )


def decode_if_needed(text):
    if type(text) is bytes:
        return text.decode(encoding='utf-8')
    else:
        return text


def render_markdown(filename, title=None):
    """
    Renders a markdown file to html
    :param filename: A markdown file to render
    :return: HTML version of the markdown file
    """
    app = flask.current_app
    for app_open in [app.open_instance_resource, app.open_resource, open]:
        try:
            with app_open(filename) as f:
                text = decode_if_needed(f.read())
                break
        except FileNotFoundError:
            ...
    else:
        text = f'# File not found\n\n{filename} is not found\n'

    text = markdown.markdown(text)
    return flask.render_template('markdown.html', markdown_content=flask.Markup(text), title=title)
