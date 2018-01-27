from plone.app.textfield import RichText
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.app.z3cform.widget import RichTextFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from yafowil.base import factory
from z3c.relationfield.schema import RelationList
from zope.schema import ASCIILine
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Datetime
from zope.schema import Text
from zope.schema import TextLine
from zope.schema import Tuple


class widget_factory(object):
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
        :param field: namedtuple containing schema field definition
        :return object: yafowil.Widget instance
        """
        # widget bound factory
        if field.widget:
            return cls._registry[field.widget.factory](context, field)
        # schema field bound factory
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


###############################################################################
# schema field bound factories
###############################################################################

@widget_factory(RichText)
def rich_text_widget_factory(context, field):
    return factory(
        '#field:richtext',
        props={
            'label': field.name
        })


@widget_factory(RelationList)
def relation_list_widget_factory(context, field):
    return factory(
        '#field:select',
        props={
            'label': field.name,
            'vocabulary': [1, 2, 3]
        })


@widget_factory(ASCIILine)
def ascii_line_widget_factory(context, field):
    return factory(
        '#field:text',
        props={
            'label': field.name
        })


@widget_factory(Bool)
def bool_widget_factory(context, field):
    return factory(
        '#field:checkbox',
        props={
            'label': field.name
        })


@widget_factory(Choice)
def choice_widget_factory(context, field):
    return factory(
        '#field:select',
        props={
            'label': field.name,
            'vocabulary': [1, 2, 3]
        })


@widget_factory(Datetime)
def datetime_widget_factory(context, field):
    return factory(
        '#field:datetime',
        props={
            'label': field.name
        })


@widget_factory(Text)
def text_widget_factory(context, field):
    return factory(
        '#field:textarea',
        props={
            'label': field.name
        })


@widget_factory(TextLine)
def text_line_widget_factory(context, field):
    return factory(
        '#field:text',
        props={
            'label': field.name
        })


@widget_factory(Tuple)
def tuple_widget_factory(context, field):
    return factory(
        '#field:select',
        props={
            'label': field.name,
            'vocabulary': [1, 2, 3]
        })


###############################################################################
# widget bound factories
###############################################################################

@widget_factory(RichTextFieldWidget)
def rich_text_field_widget_factory(context, field):
    return factory(
        '#field:select',
        props={
            'label': field.name,
            'vocabulary': [1, 2, 3]
        })


@widget_factory(DatetimeFieldWidget)
def datetime_field_widget_factory(context, field):
    return factory(
        '#field:select',
        props={
            'label': field.name,
            'vocabulary': [1, 2, 3]
        })


@widget_factory(AjaxSelectFieldWidget)
def ajax_select_field_widget_factory(context, field):
    return factory(
        '#field:select',
        props={
            'label': field.name,
            'vocabulary': [1, 2, 3]
        })


@widget_factory(SelectFieldWidget)
def select_field_widget_factory(context, field):
    return factory(
        '#field:select',
        props={
            'label': field.name,
            'vocabulary': [1, 2, 3]
        })


@widget_factory(RelatedItemsFieldWidget)
def related_items_field_widget_factory(context, field):
    return factory(
        '#field:select',
        props={
            'label': field.name,
            'vocabulary': [1, 2, 3]
        })
