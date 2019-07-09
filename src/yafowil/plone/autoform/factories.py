# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from node.utils import UNSET
from plone.app.textfield import RichText
from plone.app.widgets.base import dict_merge
from plone.app.widgets.utils import get_ajaxselect_options
from plone.app.widgets.utils import get_relateditems_options
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import DateFieldWidget
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.app.z3cform.widget import RichTextFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.formwidget.recurrence.z3cform.widget import RecurrenceFieldWidget
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from yafowil.base import factory
from yafowil.plone.autoform import FORM_SCOPE_ADD
from yafowil.plone.autoform import FORM_SCOPE_DISPLAY
from yafowil.plone.autoform import FORM_SCOPE_EDIT
from yafowil.plone.autoform import FORM_SCOPE_HOSTILE_ATTR
from yafowil.plone.autoform.persistence import AjaxSelectPersistWriter
from yafowil.plone.autoform.persistence import RelatedItemsPersistWriter
from yafowil.plone.autoform.persistence import RichtextPersistWriter
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget
from z3c.form.browser.text import TextFieldWidget
from z3c.form.browser.textlines import TextLinesFieldWidget
from z3c.relationfield.schema import RelationList
from zope.component import getUtility
from zope.component import queryUtility
from zope.schema import ASCIILine
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Datetime
from zope.schema import Text
from zope.schema import TextLine
from zope.schema import Tuple
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.schema.interfaces import ISequence
from zope.schema.interfaces import IVocabulary
from zope.schema.interfaces import IVocabularyFactory
import logging
import six


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
                    return default_factory(aq_parent(context))
                return default_factory()
            except Exception:
                logger.exception('Fetching default_factory failed')
        return UNSET
    elif scope in [FORM_SCOPE_EDIT, FORM_SCOPE_DISPLAY]:
        if field.is_behavior:
            return getattr(field.schema(context), field.name, UNSET)
        return getattr(context, field.name, UNSET)
    return UNSET


def lookup_schema_vocabulary(context, field):
    """Lookup schema vocabulary for field.

    :param context: Context the form gets rendered on.
    :param field: ``yafowil.plone.autoform.schema.Field`` instance.
    :return: ``zope.schema.interfaces.IVocabulary`` implementation.
    """
    vocabulary = None
    # try to find vocabulary on widget params
    if field.widget:
        vocabulary = field.widget.params.get('vocabulary')
    # try to find vocabulary at schemafield.vocabulary if not found on widget
    if not vocabulary:
        vocabulary = getattr(field.schemafield, 'vocabulary', vocabulary)
    # try to find vocabulary at schemafield.vocabularyName if still not found
    if not vocabulary:
        vocabulary = getattr(field.schemafield, 'vocabularyName', vocabulary)
    # return empty list if no vocabulary found
    if not vocabulary:
        return None
    # try to lookup vocabulary by name
    if isinstance(vocabulary, six.string_types):
        vocabulary = queryUtility(IVocabularyFactory, vocabulary)
    # call vocabulary factory with context
    if IVocabularyFactory.providedBy(vocabulary):
        vocabulary = vocabulary(context)
    # return vocab
    if IVocabulary.providedBy(vocabulary):
        return vocabulary
    # lookup failed
    raise ValueError('lookup_schema_vocabulary(): {0}'.format(vocabulary))


def lookup_vocabulary(context, field):
    """Lookup vocabulary for field which can be used with yafowil factory.

    :param context: Context the form gets rendered on.
    :param field: ``yafowil.plone.autoform.schema.Field`` instance.
    :return: Vocabulary suitable for yafowil factory.
    """
    vocabulary = lookup_schema_vocabulary(context, field)
    ret = list()
    if not vocabulary:
        return ret
    for term in vocabulary:
        ret.append((term.token, term.title))
    return ret


###############################################################################
# schema field bound factories
###############################################################################

@widget_factory(RichText)
def rich_text_widget_factory(context, field):
    return factory(
        '#field:plonerichtext',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'persist': True,
            'persist_writer': RichtextPersistWriter(field),
            'default': field.schemafield.missing_value,
            'context': context
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
            'required': field.required,
            'locale': 'de',  # XXX
            'datepicker': True,
            'time': True,
            'timepicker': True,
            'persist': True,
            'emptyvalue': None
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

@widget_factory(SingleCheckBoxFieldWidget)
def single_checkbox_field_widget_factory(context, field):
    return factory(
        '#field:checkbox',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'checkbox.class_add': field.widget.params.get('klass')
        },
        mode=field.mode)


@widget_factory(TextFieldWidget)
def text_field_widget_factory(context, field):
    return factory(
        '#field:text',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'text.class_add': field.widget.params.get('klass')
        },
        mode=field.mode)


@widget_factory(TextLinesFieldWidget)
def text_lines_field_widget_factory(context, field):
    return factory(
        '#field:textarea',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'textarea.class_add': field.widget.params.get('klass')
        },
        mode=field.mode)


@widget_factory(RichTextFieldWidget)
def rich_text_field_widget_factory(context, field):
    return factory(
        '#field:plonerichtext',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'persist': True,
            'persist_writer': RichtextPersistWriter(field),
            'pattern_options': field.widget.params.get('pattern_options'),
            'default': field.schemafield.missing_value,
            'context': context
        },
        mode=field.mode)


@widget_factory(DateFieldWidget)
def date_field_widget_factory(context, field):
    return factory(
        '#field:plonedatetime',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'include_time': False,
            'plonedatetime.class_add': field.widget.params.get('klass'),
        },
        mode=field.mode)


@widget_factory(DatetimeFieldWidget)
def datetime_field_widget_factory(context, field):
    return factory(
        '#field:plonedatetime',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'include_time': True,
            'default_timezone': field.widget.params.get('default_timezone'),
            'plonedatetime.class_add': field.widget.params.get('klass'),
        },
        mode=field.mode)


@widget_factory(RecurrenceFieldWidget)
def recurrence_field_widget_factory(context, field):
    return factory(
        '#field:recurrence',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'recurrence.class_add': field.widget.params.get('klass'),
            'start_field': field.widget.params.get('start_field'),
            'first_day': field.widget.params.get('first_day'),
            'show_repeat_forever': field.widget.params.get('show_repeat_forever'),
        },
        mode=field.mode)


@widget_factory(AjaxSelectFieldWidget)
def ajax_select_field_widget_factory(context, field):
    # XXX: add and use ploneselect2 blueprint in yafowil.plone.widgets.select2
    # XXX: generalize schemafield and vocabulary lookups
    # Pattern options logic taken from
    # ``plone.app.z3cform.widget.AjaxSelectWidget``.
    # widget options
    widget = field.widget
    separator = widget.params.get('separator', ';')
    orderable = widget.params.get('orderable', False)
    vocabulary_view = widget.params.get('vocabulary_view', '@@getVocabulary')
    vocabulary_name = widget.params['vocabulary']
    value = value_or_default(context, field)
    value = separator.join(value) if value else ''
    # pattern options
    opts = dict()
    schemafield = None
    if IChoice.providedBy(field.schemafield):
        opts['maximumSelectionSize'] = 1
        schemafield = field.schemafield
    elif ICollection.providedBy(field.schemafield):
        schemafield = field.schemafield.value_type
    if IChoice.providedBy(schemafield):
        opts['allowNewItems'] = 'false'
    opts = dict_merge(
        get_ajaxselect_options(
            context,
            value,
            separator,
            vocabulary_name,
            vocabulary_view,
            field_name=field.name
        ),
        opts
    )
    # get ajax vocabulary
    if schemafield and getattr(schemafield, 'vocabulary', None):
        # e.g. 'form.widgets.IDublinCore.subjects'
        # XXX: taken from the z3c form implementation, actually a hack
        #      getSource would need to be overwritten with an own implementation
        # XXX: check how getSource refers to field name
        widget_name = 'form.widgets.{}.{}'.format(
            field.schemafield.name,
            field.name
        )
        source_url = '{0:s}/++widget++{1:s}/@@getSource'.format(
            context.REQUEST.getURL(),
            widget_name
        )
        opts['vocabularyUrl'] = source_url
    # ISequence represents an orderable collection
    if ISequence.providedBy(field.schemafield) or orderable:
        opts['orderable'] = True
    # hardcoded security check hack for keywords.
    # XXX: needs to be generalized
    if vocabulary_name == 'plone.app.vocabularies.Keywords':
        membership = getToolByName(context, 'portal_membership')
        user = membership.getAuthenticatedMember()
        registry = getUtility(IRegistry)
        roles_allowed_to_add_keywords = registry.get(
            'plone.roles_allowed_to_add_keywords',
            []
        )
        roles = set(user.getRolesInContext(context))
        allowNewItems = 'false'
        if roles.intersection(roles_allowed_to_add_keywords):
            allowNewItems = 'true'
        opts['allowNewItems'] = allowNewItems
    # call yafowil factory
    return factory(
        '#field:text',
        value=value,
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'text.class_add': 'pat-select2',
            'text.data': {
                'pat-select2': opts
            },
            'persist_writer': AjaxSelectPersistWriter(field)
        },
        mode=field.mode)


@widget_factory(SelectFieldWidget)
def select_field_widget_factory(context, field):
    # XXX: add and use ploneselect2 blueprint in yafowil.plone.widgets.select2
    # XXX: check whether choice schema field uses this widget by default
    # Pattern options logic taken from ``plone.app.z3cform.widget.SelectFieldWidget``.
    # ``SelectFieldWidget`` inherits from ``plone.app.widgets.base.SelectWidget``.
    # widget options
    widget = field.widget
    separator = widget.params.get('separator', ';')
    # noValueToken = widget.params.get('noValueToken', u'')
    # noValueMessage = widget.params.get('noValueMessage', u'')
    multiple = widget.params.get('multiple', None)
    orderable = widget.params.get('orderable', False)
    required = field.required
    # pattern options
    opts = dict()
    if multiple or ICollection.providedBy(field.schemafield):
        multiple = opts['multiple'] = True
    # ISequence represents an orderable collection
    if orderable or ISequence.providedBy(field.schemafield):
        opts['orderable'] = True
    if multiple:
        opts['separator'] = separator
    # Allow to clear field value if it is not required
    if not required:
        opts['allowClear'] = True
    # vocabulary for selection
    vocab = lookup_vocabulary(context, field)
    # call yafowil factory
    return factory(
        '#field:select',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'vocabulary': vocab,
            'select.class_add': 'pat-select2',
            'select.data': {
                'pat-select2': opts
            }
        },
        mode=field.mode)


@widget_factory(RelatedItemsFieldWidget)
def related_items_field_widget_factory(context, field):
    # XXX: use relation blueprint from yafowil.plone.widgets.relation
    # XXX: generalize schemafield and vocabulary lookups
    # Pattern options logic taken from ``plone.app.z3cform.widget.RelatedItemsWidget``.
    # widget options
    widget = field.widget
    separator = widget.params.get('separator', ';')
    vocabulary_view = widget.params.get('vocabulary_view', '@@getVocabulary')
    vocabulary_name = widget.params.get('vocabulary', 'plone.app.vocabularies.Catalog')
    # orderable = widget.params.get('orderable', False)
    vocabulary_override = False
    schemafield = None
    if IChoice.providedBy(field.schemafield):
        schemafield = field.schemafield
    elif ICollection.providedBy(field.schemafield):
        schemafield = field.schemafield.value_type
    if (
        not vocabulary_name and
        schemafield is not None and
        getattr(schemafield, 'vocabularyName', None)
    ):
        vocabulary_name = field.vocabularyName
        vocabulary_override = True
    # field value
    value = value_or_default(context, field)
    value = separator.join([IUUID(o.to_object) for o in value]) if value else ''
    # pattern options
    opts = dict()
    if IChoice.providedBy(field.schemafield):
        opts['maximumSelectionSize'] = 1
    # XXX: check where original implementation gets ``mode`` and ``basePath``
    #      from. probably ``widget.params``
    root_search_mode = opts.get('mode', None) and 'basePath' not in opts
    opts = dict_merge(
        get_relateditems_options(
            context,
            value,
            separator,
            vocabulary_name,
            vocabulary_view,
            field_name=field.name,
        ),
        opts,
    )
    if root_search_mode:
        # Delete default basePath option in search mode, when no basePath
        # was explicitly set.
        del opts['basePath']
    if not vocabulary_override \
            and schemafield \
            and getattr(schemafield, 'vocabulary', None):
        # widget vocab takes precedence over field
        form_url = context.REQUEST.getURL()
        # e.g. 'form.widgets.IDublinCore.subjects'
        # XXX: taken from the z3c form implementation, actually a hack
        #      getSource would need to be overwritten with an own implementation
        # XXX: check how getSource refers to field name
        widget_name = 'form.widgets.{}.{}'.format(
            field.schemafield.name,
            field.name
        )
        source_url = '{0:s}/++widget++{1:s}/@@getSource'.format(
            form_url,
            widget_name,
        )
        opts['vocabularyUrl'] = source_url
    # call yafowil factory
    return factory(
        '#field:text',
        value=value,
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'text.class_add': 'pat-relateditems',
            'text.data': {
                'pat-relateditems': opts
            },
            'persist_writer': RelatedItemsPersistWriter(field)
        },
        mode=field.mode)
