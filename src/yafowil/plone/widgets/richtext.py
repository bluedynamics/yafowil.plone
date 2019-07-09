from yafowil.base import factory
from yafowil.common import generic_extractor
from yafowil.common import generic_required_extractor
from yafowil.common import textarea_renderer
from yafowil.utils import as_data_attrs
from yafowil.utils import attr_value
from yafowil.utils import cssid
from yafowil.utils import managedprops
from zope.component import getMultiAdapter
import json


def richtext_display_renderer(widget, data):
    value = widget.getter
    if value:
        value = value.raw
    else:
        value = ''
    return data.tag('div', value, **{'class': 'display-richtext'})


@managedprops('context', 'pattern_options', 'default')
def richtext_edit_renderer(widget, data):
    value = widget.getter
    if value:
        data.value = value.raw
    rendered = textarea_renderer(widget, data)
    optiontags = []
    for mimetype in ['text/html', 'text/x-web-textile']:
        optiontags.append(data.tag('option', mimetype))
    context = attr_value('context', widget, data)
    if context is None:
        raise ValueError(u'Richtext blueprint needs a context to work')
    pattern_options = getMultiAdapter(
        (context, context.REQUEST, widget),
        name='plone_settings'
    ).tinymce()['data-pat-tinymce']
    pattern_options_dict = json.loads(pattern_options)
    pattern_options_overrides = attr_value('pattern_options', widget, data)
    if pattern_options_overrides:
        pattern_options_dict.update(pattern_options_overrides)
    select_attrs = {
        'name_': '{}.mimetype'.format(widget.dottedpath),
        'id': cssid(widget, 'input.mimetype'),
        'class': 'pat-textareamimetypeselector'
    }
    select_attrs.update(as_data_attrs({
        'pat-textareamimetypeselector': {
            'textareaName': widget.dottedpath,
            'widgets': {
                'text/html': {
                    'pattern': 'tinymce',
                    'patternOptions': pattern_options_dict
                },
            },
        }
    }))
    rendered += data.tag('select', *optiontags, **select_attrs)
    return rendered


factory.register(
    'plonerichtext',
    extractors=[
        generic_extractor,
        generic_required_extractor
    ],
    edit_renderers=[richtext_edit_renderer],
    display_renderers=[richtext_display_renderer]
)

factory.doc['blueprint']['plonerichtext'] = """\
Richtext blueprint.
"""

factory.defaults['plonerichtext.default'] = ''

factory.defaults['plonerichtext.context'] = None

factory.defaults['plonerichtext.pattern_options'] = {}
