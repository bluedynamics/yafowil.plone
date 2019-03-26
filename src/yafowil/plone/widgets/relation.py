from plone.app.widgets.base import dict_merge
from plone.app.widgets.utils import get_relateditems_options
# from Products.CMFPlone import PloneMessageFactory as _
from yafowil.base import factory
from yafowil.common import input_generic_renderer
from yafowil.utils import attr_value
from yafowil.utils import managedprops
# from yafowil.utils import UNSET


@managedprops(
    'context', 'separator', 'vocabulary_view', 'vocabulary',
    'multivalued', 'root_search_mode')
def relation_edit_renderer(widget, data):
    context = attr_value('context', widget, data)
    if context is None:
        raise ValueError(u'Relation blueprint needs a context to work')
    separator = attr_value('separator', widget, data)
    vocabulary_view = attr_value('vocabulary_view', widget, data)
    vocabulary_name = attr_value('vocabulary', widget, data)
    multivalued = attr_value('multivalued', widget, data)
    root_search_mode = attr_value('root_search_mode', widget, data)
    value = ''
    # pattern options
    opts = dict()
    if multivalued:
        opts['maximumSelectionSize'] = 1
    opts = dict_merge(
        get_relateditems_options(
            context,
            value,
            separator,
            vocabulary_name,
            vocabulary_view,
            # field_name=widget.dottedpath,
            field_name=widget.name,
        ),
        opts,
    )
    if root_search_mode:
        del opts['basePath']
    pattern_name = attr_value('pattern_name', widget, data)
    widget.attrs['class_add'] = pattern_name
    widget.attrs['data'] = {
        pattern_name: opts
    }
    return input_generic_renderer(widget, data)


def relation_display_renderer(widget, data):
    return '<div>Relation</div>'


factory.register(
    'relation',
    edit_renderers=[relation_edit_renderer],
    display_renderers=[relation_display_renderer])


factory.doc['blueprint']['relation'] = """\
Relation blueprint.
"""

factory.defaults['relation.class'] = 'relateditems'

factory.defaults['relation.pattern_name'] = 'pat-relateditems'

factory.defaults['relation.context'] = None

factory.defaults['relation.separator'] = ';'

factory.defaults['relation.vocabulary_view'] = '@@getVocabulary'

factory.defaults['relation.vocabulary'] = 'plone.app.vocabularies.Catalog'

factory.defaults['relation.multivalued'] = False

factory.defaults['relation.root_search_mode'] = False
