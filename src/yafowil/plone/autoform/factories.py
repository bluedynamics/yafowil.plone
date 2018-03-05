from node.utils import UNSET
from plone.app.textfield import RichText
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.app.z3cform.widget import RichTextFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from yafowil.base import factory
from yafowil.plone.autoform import FORM_SCOPE_ADD
from yafowil.plone.autoform import FORM_SCOPE_EDIT
from yafowil.plone.autoform import FORM_SCOPE_HOSTILE_ATTR
from z3c.relationfield.schema import RelationList
from zope.schema import ASCIILine
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Datetime
from zope.schema import Text
from zope.schema import TextLine
from zope.schema import Tuple
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.vocabulary import SimpleVocabulary
import logging


logger = logging.getLogger('yafowil.plone')


class widget_factory(object):
    """Decorator and registry for zope.schema related yafowil widget factories.
    """
    _registry = dict()

    def __init__(self, ob):
        """Initialize widget_factory decorator for object.

        :param ob: Schema field class, z3cform widget class or schema
            field instance.
        """
        self.ob = ob

    def __call__(self, ob):
        """Register widget factory callback.

        :param ob: Callable accepting context and field arguments passed to
            ``widget_factory.widget_for``.
        """
        self._registry[self.ob] = ob
        return ob

    @classmethod
    def widget_for(cls, context, field):
        """Create and return yafowil widget for field by calling factory
        registered with ``widget_factory`` for field.

        :param context: Context the form gets rendered on.
        :param field: ``yafowil.plone.autoform.schema.Field`` instance.
        :return object: yafowil.Widget instance
        """
        return cls._lookup_factory(field)(context, field)

    @classmethod
    def _lookup_factory(cls, field):
        """Looup factory for field.

        :param field: ``yafowil.plone.autoform.schema.Field`` instance.
        :return object: Callable accepting ``context`` and ``field`` as
            arguments .
        """
        # dedicated schema field bound factory
        if field.schemafield in cls._registry:
            factory = cls._registry[field.schemafield]
        # widget bound factory
        elif field.widget:
            factory = cls._registry[field.widget.factory]
        # schema field bound factory
        else:
            factory = cls._registry[field.schemafield.__class__]
        return factory


def value_or_default(context, field):
    """Lookup value or default value for field.

    :param context: Context the form gets rendered on.
    :param field: ``yafowil.plone.autoform.schema.Field`` instance.
    :return: Value or default.
    """
    request = context.REQUEST
    scope = getattr(request, FORM_SCOPE_HOSTILE_ATTR, None)
    if scope == FORM_SCOPE_ADD:
        default_factory = field.schemafield.defaultFactory
        if default_factory:
            try:
                if IContextAwareDefaultFactory.providedBy(default_factory):
                    return default_factory(context)
                return default_factory()
            except Exception:
                logger.exception('Fetching default_factory failed')
        return UNSET
    elif scope == FORM_SCOPE_EDIT:
        if field.is_behavior:
            return getattr(field.schema(context), field.name, UNSET)
        return getattr(context, field.name, UNSET)
    return UNSET


def lookup_vocabulary(context, field):
    """Lookup vocabulary for field.

    :param context: Context the form gets rendered on.
    :param field: ``yafowil.plone.autoform.schema.Field`` instance.
    :return: Vocabulary suitable for yafowil factory.
    """
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
            'label': field.label,
            'help': field.help,
            'required': field.required
        },
        mode=field.mode)


@widget_factory(RelationList)
def relation_list_widget_factory(context, field):
    return factory(
        '#field:select',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'vocabulary': lookup_vocabulary(context, field)
        },
        mode=field.mode)


@widget_factory(ASCIILine)
def ascii_line_widget_factory(context, field):
    return factory(
        '#field:text',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required
        },
        mode=field.mode)


@widget_factory(Bool)
def bool_widget_factory(context, field):
    return factory(
        '#field:checkbox',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'plonelabel.position': 'after'
        },
        mode=field.mode)


@widget_factory(Choice)
def choice_widget_factory(context, field):
    return factory(
        '#field:select',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'vocabulary': lookup_vocabulary(context, field)
        },
        mode=field.mode)


@widget_factory(Datetime)
def datetime_widget_factory(context, field):
    return factory(
        '#field:datetime',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required
        },
        mode=field.mode)


@widget_factory(Text)
def text_widget_factory(context, field):
    return factory(
        '#field:textarea',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required
        },
        mode=field.mode)


@widget_factory(TextLine)
def text_line_widget_factory(context, field):
    return factory(
        '#field:text',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required
        },
        mode=field.mode)


@widget_factory(Tuple)
def tuple_widget_factory(context, field):
    return factory(
        '#field:select',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'vocabulary': lookup_vocabulary(context, field)
        },
        mode=field.mode)


###############################################################################
# widget bound factories
###############################################################################

@widget_factory(RichTextFieldWidget)
def rich_text_field_widget_factory(context, field):
    return factory(
        '#field:richtext',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required
        },
        mode=field.mode)


@widget_factory(DatetimeFieldWidget)
def datetime_field_widget_factory(context, field):
    return factory(
        '#field:datetime',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required
        },
        mode=field.mode)


@widget_factory(AjaxSelectFieldWidget)
def ajax_select_field_widget_factory(context, field):
    return factory(
        '#field:autocomplete',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'source': 'foooo'
        },
        mode=field.mode)


@widget_factory(SelectFieldWidget)
def select_field_widget_factory(context, field):
    return factory(
        '#field:select',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'vocabulary': lookup_vocabulary(context, field)
        },
        mode=field.mode)


@widget_factory(RelatedItemsFieldWidget)
def related_items_field_widget_factory(context, field):
    return factory(
        '#field:select',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'vocabulary': lookup_vocabulary(context, field)
        },
        mode=field.mode)
