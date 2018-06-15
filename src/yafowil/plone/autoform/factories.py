from node.utils import UNSET
from plone.app.textfield import RichText
from plone.app.widgets.base import dict_merge
from plone.app.widgets.utils import get_ajaxselect_options
from plone.app.widgets.utils import get_tinymce_options
from plone.app.widgets.utils import get_widget_form
from plone.app.z3cform.widget import AjaxSelectFieldWidget
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.app.z3cform.widget import RelatedItemsFieldWidget
from plone.app.z3cform.widget import RichTextFieldWidget
from plone.app.z3cform.widget import SelectFieldWidget
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from yafowil.base import factory
from yafowil.plone.autoform import FORM_SCOPE_ADD
from yafowil.plone.autoform import FORM_SCOPE_EDIT
from yafowil.plone.autoform import FORM_SCOPE_HOSTILE_ATTR
#from z3c.form.interfaces import IEditForm
#from z3c.form.interfaces import IForm
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
    if isinstance(vocabulary, basestring):
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


def create_richtext_widget(context, field):
    """Reads tinymce pattern options and creates a richtext field using related
    mockup pattern.
    """
    def mimetypes_data(widget, data):
        opts = get_tinymce_options(context, field.schemafield, context.REQUEST)
        return {
            'pat-textareamimetypeselector': {
                'textareaName': widget.dottedpath,
                'widgets': {
                    'text/html': {
                        'pattern': 'tinymce',
                        'patternOptions': opts
                    },
                },
            }
        }
    return factory(
        '#field:richtext',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'mimetypes': ['text/html', 'text/x-web-textile'],
            'mimetypes_class': 'pat-textareamimetypeselector',
            'mimetypes_data': mimetypes_data
        },
        mode=field.mode)


def create_datetime_widget(context, field):
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
            'timepicker': True
        },
        mode=field.mode)


###############################################################################
# schema field bound factories
###############################################################################

@widget_factory(RichText)
def rich_text_widget_factory(context, field):
    return create_richtext_widget(context, field)


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
    return create_datetime_widget(context, field)


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
    # XXX: insert pat options logic from RichTextFieldWidget here
    # XXX: check if RichText schema field also uses this widget
    return create_richtext_widget(context, field)


@widget_factory(DatetimeFieldWidget)
def datetime_field_widget_factory(context, field):
    # XXX: use datetime pattern from mockup here
    # XXX: insert pattern option logic from DatetimeFieldWidget here
    # XXX: check if datetime schema field also uses this widget by default
    return create_datetime_widget(context, field)


@widget_factory(AjaxSelectFieldWidget)
def ajax_select_field_widget_factory(context, field):
    # Pattern options logic taken from
    # ``plone.app.z3cform.widget.AjaxSelectWidget``.
    # XXX: pass view and request to widget factories
    request = context.REQUEST
    value = value_or_default(context, field)
    separator = ';'
    orderable = False
    vocabulary_view = '@@getVocabulary'
    vocabulary_name = field.widget.params['vocabulary']

    view_ctx = context
    # XXX: view_ctx = get_widget_form(view)
    # For EditForms and non-Forms (in tests), the vocabulary is looked
    # up on the context, otherwise on the view
    # XXX: check for yafowil form instead of z3c form
    #if (IEditForm.providedBy(view_ctx) or not IForm.providedBy(view_ctx)):
    #    view_ctx = context
    # pattern options

    opts = dict()
    schemafield = None
    if IChoice.providedBy(field.schemafield):
        opts['maximumSelectionSize'] = 1
        schemafield = field.schemafield
    elif ICollection.providedBy(field.schemafield):
        schemafield = field.schemafield.value_type
    if IChoice.providedBy(field):
        opts['allowNewItems'] = 'false'

    opts = dict_merge(
        get_ajaxselect_options(
            view_ctx,
            value,
            separator,
            vocabulary_name,
            vocabulary_view,
            field_name=field.name
        ),
        opts
    )

    if schemafield and not vocabulary_name:
        form_url = request.getURL()
        # e.g. 'form.widgets.IDublinCore.subjects'
        # XXX: taken from the z3c form implementation, actually a hack
        #      getSource would need to be overwritten with an own implementation
        widget_name = 'form.widgets.{}.{}'.format(
            field.schemafield.name,
            field.name
        )
        source_url = '{0:s}/++widget++{1:s}/@@getSource'.format(
            form_url,
            widget_name,
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

    # data attribute data
    data = {
        'pat-select2': opts
    }

    return factory(
        '#field:text',
        value=value,
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'class_add': 'pat-select2',
            'data': data
        },
        mode=field.mode)


@widget_factory(SelectFieldWidget)
def select_field_widget_factory(context, field):
    # XXX: check whether choice schema field uses this widget by default
    separator = ';'
    noValueToken = u''
    noValueMessage = u''
    multiple = None  # XXX: somewhere from widget?
    orderable = False
    required = field.required

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

    vocab = lookup_vocabulary(context, field)

    # XXX: this can probably be deleted
    #base_items = self.items
    #if callable(base_items):
        # items used to be a property in all widgets, then in the select
        # widget it became a method, then in a few others too, but never in
        # all, so this was reverted to let it be a property again.  Let's
        # support both here to avoid breaking on some z3c.form versions.
        # See https://github.com/zopefoundation/z3c.form/issues/44
    #    base_items = base_items()
    #items = []
    #for item in base_items:
    #    if not isinstance(item['content'], six.string_types):
    #        item['content'] = translate(
    #            item['content'],
    #            context=self.request,
    #            default=item['value'])
    #    items.append((item['value'], item['content']))
    #args['items'] = items

    data = {
        'pat-select2': opts
    }

    return factory(
        '#field:select',
        value=value_or_default(context, field),
        props={
            'label': field.label,
            'help': field.help,
            'required': field.required,
            'vocabulary': vocab,
            'class_add': 'pat-select2',
            'data': data
        },
        mode=field.mode)


@widget_factory(RelatedItemsFieldWidget)
def related_items_field_widget_factory(context, field):
    pattern = 'relateditems'
    separator = ';'
    vocabulary = None
    vocabulary_override = False
    vocabulary_view = '@@getVocabulary'
    orderable = False
    opts = dict()

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
