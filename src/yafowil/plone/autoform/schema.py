from collections import namedtuple
from plone.app.textfield import RichText
from plone.autoform.interfaces import WIDGETS_KEY
from plone.autoform.utils import mergedTaggedValueDict
from plone.autoform.utils import mergedTaggedValueList
from plone.supermodel.interfaces import DEFAULT_ORDER
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from yafowil.base import factory
from z3c.relationfield.schema import RelationList
from zope.schema import ASCIILine
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Datetime
from zope.schema import Text
from zope.schema import TextLine
from zope.schema import Tuple
from zope.schema import getFieldsInOrder


Field = namedtuple('Field', ['name', 'schemafield', 'schema', 'widget', 'mode'])


def resolve_schemata(schemata):
    """Resove zope interface schemata for content type to fieldsets and
    fields definitions for further processing.
    """
    # fieldset definitions
    fieldsets = dict()
    # field definitions
    fields = dict()
    # create default fieldset, not resolved by plone.autoform
    fieldsets['default'] = Fieldset(
        'default',
        label='Default' # XXX: i18n
    )
    for schema in schemata:
        # collect all fieldsets from schema
        consumed_fields = set()
        schema_fieldsets = mergedTaggedValueList(schema, FIELDSETS_KEY)
        for schema_fieldset in schema_fieldsets:
            fieldset = fieldsets.setdefault(
                schema_fieldset.__name__,
                Fieldset(
                    schema_fieldset.__name__,
                    label=schema_fieldset.label
                )
            )
            if schema_fieldset.order != DEFAULT_ORDER:
                fieldset.order = schema_fieldset.order
            if (
                schema_fieldset.label != fieldset.label and
                schema_fieldset.label != fieldset.__name__
            ):
                fieldset.label = schema_fieldset.label
            if schema_fieldset.description is not None:
                fieldset.description = schema_fieldset.description
            for field_name in schema_fieldset.fields:
                fieldset.fields.append(field_name)
                consumed_fields.add(field_name)
        # collect all fields from schema and add field to return value and
        # fieldname to default fieldset if not already consumed
        for name, schemafield in getFieldsInOrder(schema):
            fields[name] = Field(
                name=name,
                schemafield=schemafield,
                schema=schema,
                widget=None,  # XXX: if widget defined for schema field
                mode='edit'
            )
            if name not in consumed_fields:
                fieldsets['default'].fields.append(name)
        # XXX:
        ##widgets = mergedTaggedValueDict(schema, WIDGETS_KEY)
    return {
        'fieldsets': fieldsets,
        'fields': fields,
    }


class schema_widget_factory(object):
    """Decorator and registry for zope.schema related yafowil widget factories
    """
    _registry = dict()

    def __init__(self, cls):
        self.cls = cls

    def __call__(self, ob):
        self._registry[self.cls] = ob
        return ob

    @classmethod
    def widget_for(cls, context, field):
        """Create and return yafowil widget for field.

        :param context: Context the form gets rendered on
        :param field: Dict containing schema field definition
        :return object: yafowil.Widget instance
        """
        return cls._registry[field.schemafield.__class__](context, field)


"""
zope.schema.field

['_Element__tagged_values', '_Field__missing_value_marker', '__class__', 
'__delattr__', '__dict__', '__doc__', '__eq__', '__format__', 
'__getattribute__', '__hash__', '__implemented__', '__init__', '__module__', 
'__name__', '__ne__', '__new__', '__providedBy__', '__provides__', 
'__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', 
'__str__', '__subclasshook__', '__weakref__', '_type', '_validate', 
'bind', 'constraint', 'context', 'default', 'defaultFactory', 'description', 
'fromUnicode', 'get', 'getDoc', 'getName', 'getTaggedValue', 
'getTaggedValueTags', 'interface', 'max_length', 'min_length', 'missing_value', 
'order', 'query', 'queryTaggedValue', 'readonly', 'required', 'set', 
'setTaggedValue', 'title', 'validate']
"""


@schema_widget_factory(RichText)
def rich_text_widget_factory(context, field):
    return factory(
        '#field:richtext',
        props={
            'label': field.name
        })


@schema_widget_factory(RelationList)
def relation_list_widget_factory(context, field):
    return factory(
        '#field:select',
        props={
            'label': field.name,
            'vocabulary': [1, 2, 3]
        })


@schema_widget_factory(ASCIILine)
def ascii_line_widget_factory(context, field):
    return factory(
        '#field:text',
        props={
            'label': field.name
        })


@schema_widget_factory(Bool)
def bool_widget_factory(context, field):
    return factory(
        '#field:checkbox',
        props={
            'label': field.name
        })


@schema_widget_factory(Choice)
def choice_widget_factory(context, field):
    return factory(
        '#field:select',
        props={
            'label': field.name,
            'vocabulary': [1, 2, 3]
        })


@schema_widget_factory(Datetime)
def datetime_widget_factory(context, field):
    return factory(
        '#field:datetime',
        props={
            'label': field.name
        })


@schema_widget_factory(Text)
def text_widget_factory(context, field):
    return factory(
        '#field:textarea',
        props={
            'label': field.name
        })


@schema_widget_factory(TextLine)
def text_line_widget_factory(context, field):
    return factory(
        '#field:text',
        props={
            'label': field.name
        })


@schema_widget_factory(Tuple)
def tuple_widget_factory(context, field):
    return factory(
        '#field:select',
        props={
            'label': field.name,
            'vocabulary': [1, 2, 3]
        })
