from node.utils import UNSET
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
from zope.schema.vocabulary import SimpleVocabulary
import logging


logger = logging.getLogger('yafowil.plone')


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
            factory = cls._registry[field.widget.factory]
        # schema field bound factory
        else:
            factory = cls._registry[field.schemafield.__class__]
        return factory(context, field)


def value_or_default(context, field):
    request = context.REQUEST
    if request._yafowil_autoform_scope == 'add':
        default_factory = field.schemafield.defaultFactory
        if default_factory:
            try:
                # XXX: zope.schema.interfaces.IContextAwareDefaultFactory
                return default_factory(context)
            except Exception as e:
                logger.warning
        return UNSET
    elif request._yafowil_autoform_scope == 'edit':
        return UNSET
    else:
        return UNSET


def lookup_vocabulary(field):
    vocabulary = None
    # try to find vocabulary on widget params
    if field.widget:
        vocabulary = field.widget.params.get('vocabulary')
    # try to find vocabulary on schemafield if not found on widget
    if not vocabulary:
        if hasattr(field.schemafield, 'vocabulary'):
            vocabulary = field.schemafield.vocabulary
    # return empty list if no vocabulary found
    if not vocabulary:
        return []
    if isinstance(vocabulary, basestring):
        # XXX: try to lookup vocabulary
        return []
    if isinstance(vocabulary, SimpleVocabulary):
        ret = list()
        for term in vocabulary:
            # XXX: term.value as vocab key? probably what we want when using
            #      datatypes
            ret.append((term.token, term.title))
        return ret
    logger.warning('Unknown vocabulary type: {0}'.format(vocabulary))
    return []


###############################################################################
# schema field bound factories
###############################################################################

@widget_factory(RichText)
def rich_text_widget_factory(context, field):
    return factory(
        '#field:richtext',
        value=value_or_default(context, field),
        props={
            'label': field.schemafield.title,
            'help': field.schemafield.description,
            'required': field.schemafield.required
        })


@widget_factory(RelationList)
def relation_list_widget_factory(context, field):
    return factory(
        '#field:select',
        value=value_or_default(context, field),
        props={
            'label': field.schemafield.title,
            'help': field.schemafield.description,
            'required': field.schemafield.required,
            'vocabulary': lookup_vocabulary(field)
        })


@widget_factory(ASCIILine)
def ascii_line_widget_factory(context, field):
    return factory(
        '#field:text',
        value=value_or_default(context, field),
        props={
            'label': field.schemafield.title,
            'help': field.schemafield.description,
            'required': field.schemafield.required
        })


@widget_factory(Bool)
def bool_widget_factory(context, field):
    return factory(
        '#field:checkbox',
        value=value_or_default(context, field),
        props={
            'label': field.schemafield.title,
            'help': field.schemafield.description,
            'required': field.schemafield.required,
            'plonelabel.position': 'after'
        })


@widget_factory(Choice)
def choice_widget_factory(context, field):
    return factory(
        '#field:select',
        value=value_or_default(context, field),
        props={
            'label': field.schemafield.title,
            'help': field.schemafield.description,
            'required': field.schemafield.required,
            'vocabulary': lookup_vocabulary(field)
        })


@widget_factory(Datetime)
def datetime_widget_factory(context, field):
    return factory(
        '#field:datetime',
        value=value_or_default(context, field),
        props={
            'label': field.schemafield.title,
            'help': field.schemafield.description,
            'required': field.schemafield.required
        })


@widget_factory(Text)
def text_widget_factory(context, field):
    return factory(
        '#field:textarea',
        value=value_or_default(context, field),
        props={
            'label': field.schemafield.title,
            'help': field.schemafield.description,
            'required': field.schemafield.required
        })


@widget_factory(TextLine)
def text_line_widget_factory(context, field):
    return factory(
        '#field:text',
        value=value_or_default(context, field),
        props={
            'label': field.schemafield.title,
            'help': field.schemafield.description,
            'required': field.schemafield.required
        })


@widget_factory(Tuple)
def tuple_widget_factory(context, field):
    return factory(
        '#field:select',
        value=value_or_default(context, field),
        props={
            'label': field.schemafield.title,
            'help': field.schemafield.description,
            'required': field.schemafield.required,
            'vocabulary': lookup_vocabulary(field)
        })


###############################################################################
# widget bound factories
###############################################################################

@widget_factory(RichTextFieldWidget)
def rich_text_field_widget_factory(context, field):
    return factory(
        '#field:richtext',
        value=value_or_default(context, field),
        props={
            'label': field.schemafield.title,
            'help': field.schemafield.description,
            'required': field.schemafield.required
        })


@widget_factory(DatetimeFieldWidget)
def datetime_field_widget_factory(context, field):
    return factory(
        '#field:datetime',
        value=value_or_default(context, field),
        props={
            'label': field.schemafield.title,
            'help': field.schemafield.description,
            'required': field.schemafield.required
        })


@widget_factory(AjaxSelectFieldWidget)
def ajax_select_field_widget_factory(context, field):
    return factory(
        '#field:autocomplete',
        value=value_or_default(context, field),
        props={
            'label': field.schemafield.title,
            'help': field.schemafield.description,
            'required': field.schemafield.required,
            'source': 'foooo'
        })


@widget_factory(SelectFieldWidget)
def select_field_widget_factory(context, field):
    return factory(
        '#field:select',
        value=value_or_default(context, field),
        props={
            'label': field.schemafield.title,
            'help': field.schemafield.description,
            'required': field.schemafield.required,
            'vocabulary': lookup_vocabulary(field)
        })


@widget_factory(RelatedItemsFieldWidget)
def related_items_field_widget_factory(context, field):
    return factory(
        '#field:select',
        value=value_or_default(context, field),
        props={
            'label': field.schemafield.title,
            'help': field.schemafield.description,
            'required': field.schemafield.required,
            'vocabulary': lookup_vocabulary(field)
        })
