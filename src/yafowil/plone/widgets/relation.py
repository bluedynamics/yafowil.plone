from node.utils import UNSET
from plone.app.uuid.utils import uuidToObject
from plone.app.widgets.base import dict_merge
from plone.app.widgets.utils import get_relateditems_options
from plone.uuid.interfaces import IUUID
from yafowil.base import factory
from yafowil.common import generic_extractor
from yafowil.common import generic_required_extractor
from yafowil.common import input_generic_renderer
from yafowil.utils import attr_value
from yafowil.utils import managedprops
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


@managedprops('separator', 'multivalued')
def relation_extractor(widget, data):
    extracted = data.extracted
    if extracted is UNSET:
        return extracted
    seperator = attr_value('seperator', widget, data)
    intids = getUtility(IIntIds)
    rels = list()
    for uid in extracted.split(seperator):
        if not uid:
            continue
        try:
            to_id = intids.getId(uuidToObject(uid))
            value = RelationValue(to_id)
            rels.append(value)
        except KeyError:
            continue
    if not attr_value('multivalued', widget, data):
        return UNSET if not rels else rels[0]
    return rels


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
    # relations value
    context_value = widget.getter
    if not context_value:
        value = ''
    elif isinstance(context_value, RelationValue):
        value = IUUID(context_value.to_object)
    else:
        value = separator.join([IUUID(rel.to_object) for rel in context_value])
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
    return input_generic_renderer(widget, data, custom_attrs=dict(value=value))


def relation_link(data, ob):
    return data.tag(u'a', ob.title_or_id(), href=ob.absolute_url())


def relation_display_renderer(widget, data):
    value = widget.getter
    if not value:
        return data.tag(u'div', u'No relation selected')
    elif isinstance(value, RelationValue):
        return data.tag(u'div', relation_link(data, value.to_object))
    return data.tag(u'ul', *[relation_link(data, rel.to_object) for rel in value])


factory.register(
    'relation',
    extractors=[
        generic_extractor,
        generic_required_extractor,
        relation_extractor
    ],
    edit_renderers=[relation_edit_renderer],
    display_renderers=[relation_display_renderer]
)


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
