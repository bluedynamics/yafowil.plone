from Products.CMFPlone import PloneMessageFactory as _
from yafowil.base import factory
from yafowil.common import generic_positional_rendering_helper
from yafowil.utils import cssid
from yafowil.utils import managedprops
from yafowil.utils import UNSET


###############################################################################
# Plone specific label blueprint
###############################################################################

@managedprops('label', 'for', 'help', 'title')
def label_renderer(widget, data):
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
    label_contents = [label_text]
    if widget.attrs.get(widget.attrs['required_bullet_trigger'])\
            and data.mode == 'edit':
        label_contents.append(data.tag(
            'span', '&nbsp;',
            class_='required',
            title=_('required', 'Required')))
    label_contents.append(data.tag('span', help_text, class_='formHelp'))
    rendered = data.rendered is not UNSET and data.rendered or u''
    position = widget.attrs['position']
    if callable(position):
        position = position(widget, data)
    combined_label = u' '.join(label_contents)
    return generic_positional_rendering_helper(
        'label', combined_label, label_attrs, rendered, position, tag)


factory.register(
    'plonelabel',
    edit_renderers=[label_renderer],
    display_renderers=[label_renderer])

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
