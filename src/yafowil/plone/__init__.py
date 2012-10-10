from yafowil.base import factory
from yafowil.common import generic_positional_rendering_helper
from yafowil.utils import (
    UNSET,
    cssclasses,
    css_managed_props,
    cssid,
    managedprops,
)
from .connectors import plone_preprocessor
from Products.CMFPlone import PloneMessageFactory as _


@managedprops('label', 'for', 'help', 'title')
def plone_label_renderer(widget, data):
    tag = data.tag
    label_text = widget.attrs.get('label', widget.__name__)
    if callable(label_text):
        label_text = label_text()
    label_attrs = {'class_': 'formQuestion'}
    help_text = widget.attrs['help']
    if callable(help_text):
        help_text = help_text()
    if data.tag.translate:
        label_text = data.tag.translate(label_text)
        help_text = data.tag.translate(help_text)
    if data.mode == 'edit':
        for_path = widget.attrs['for']
        if for_path:
            for_widget = widget.root
            for name in for_path.split('.'):
                for_widget = for_widget[name]
            label_attrs['for_'] = cssid(for_widget, 'input')
        else:
            label_attrs['for_'] = cssid(widget, 'input')
        if widget.attrs['title']:
            label_attrs['title'] = widget.attrs['title']
    label_contents = label_text
    if widget.attrs.get(widget.attrs['required_bullet_trigger']) \
      and data.mode == 'edit':
        label_contents += data.tag('span', '&nbsp;',
                                   class_='required',
                                   title=_('required', 'Required'))
    label_contents += data.tag('span', help_text, class_='formHelp')
    rendered = data.rendered is not UNSET and data.rendered or u''
    position = widget.attrs['position']
    if callable(position):
        position = position(widget, data)
    return generic_positional_rendering_helper(
        'label', label_contents, label_attrs, rendered, position, tag)


factory.register(
    'plonelabel',
    edit_renderers=[plone_label_renderer],
    display_renderers=[plone_label_renderer])

factory.doc['blueprint']['plonelabel'] = """\
Label for Plone blueprint.
"""

factory.defaults['plonelabel.position'] = 'before'

factory.doc['props']['plonelabel.label'] = """\
Text to be displayed as a label.
"""

factory.defaults['plonelabel.help'] = ''
factory.doc['props']['plonelabel.help'] = """\
Help text to be displayed inside label.
"""

factory.defaults['plonelabel.title'] = None
factory.doc['props']['plonelabel.title'] = """\
Title attribute of label text
"""

factory.defaults['plonelabel.for'] = None
factory.doc['props']['plonelabel.for'] = """\
Optional dottedpath of widget to be labled
"""

factory.defaults['plonelabel.required_bullet_trigger'] = 'required'
factory.doc['props']['plonelabel.required_bullet_trigger'] = """\
Attribute name which triggers rendering of required bullet. Defaults to
'required'.
"""


PLONE_MACROS = {
    'form': {
        'chain': 'form',
        'props': {
            'form.class': 'enableUnloadProtection enableAutoFocus '
                          'enableFormTabbing edit-form',
        }
    },
    'field': {
        'chain': 'field:plonelabel:error',
        'props': {
            'field.class': 'field',
            'field.error_class': 'error',
            'error.class': 'fieldErrorBox',
            'error.render_empty': True,
            'error.position': 'before',
        }
    },
    'button': {
        'chain': 'field:submit',
        'props': {
            'field.class': 'formControls',
            'submit.class': 'context',
        }
    },

    # yafowil.widget.array
    'array': {
        'chain': 'array',
        'props': {},
    },
}


def register():
    factory.register_global_preprocessors([plone_preprocessor])
    for name, value in PLONE_MACROS.items():
        factory.register_macro(name, value['chain'], value['props'])
    factory.defaults['select.label_radio_class'] = 'radioType'
    factory.defaults['select.label_checkbox_class'] = 'checkboxType'
