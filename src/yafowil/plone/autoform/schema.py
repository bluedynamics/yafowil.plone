from collections import namedtuple
from operator import attrgetter
from plone.autoform.interfaces import WIDGETS_KEY
from plone.autoform.widgets import ParameterizedWidget
from plone.supermodel.interfaces import DEFAULT_ORDER
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from plone.supermodel.utils import mergedTaggedValueDict
from plone.supermodel.utils import mergedTaggedValueList
from yafowil.plone import _
from zope.schema import getFieldsInOrder


class _FieldSet(object):
    """Represent form fieldsets defined via ``plone.supermodel.model.fieldset``.
    All schema fields with no dedicated fieldset defined will end up in default
    fieldset.
    """

    def __init__(self, name, label='', description='', order=DEFAULT_ORDER):
        """Create fieldset.

        :param name: Fieldset name.
        :param label: Fieldset label.
        :param description: Fieldset description.
        :param order: Fieldset order.
        """
        self.name = name
        self.label = label
        self.description = description
        self.order = order
        self._children = list()

    def add(self, child):
        """Add field to fieldset.

        :param child: ``yafowil.plone.autoform.schema.Field`` or
            ``yafowil.plone.autoform.schema.Fieldset`` instance.
        """
        self._children.add(child)

    def __iter__(self):
        """Iterate over fields in order.

        :return: children iterator.
        """
        return self._children.__iter__()


class _Field(object):
    """Hold information about a field of a schema. Contained in ``FieldSet``
    instances.

    ``Field`` instances get passed to ``yafowil.plone.autoform.widget_factory``
    callbacks which are responsible to create and return ``yafowil.base.Widget``
    instances via ``yafowil.base.factory``.
    """

    def __init__(self, name, schemafield, schema, widget, mode, is_behavior):
        """Create field.

        :param name: Name of the field.
        :param schemafield: ``zope.schema._bootstrapfields.Field`` deriving
            instance.
        :param schema: ``plone.supermodel.model.Schema`` instance.
        :param widget: ``yafowil.plone.autoform.schema.Widget`` instance
        :param mode: Form widget rendering mode as string. Either 'edit',
            'display' or 'skip'
        :param is_behavior: Flag whether field belongs to a dexterity behavior.
        """
        self.name = name
        self.schemafield = schemafield
        self.schema = schema
        self.widget = widget
        self.mode = mode
        self.is_behavior = is_behavior


class _Widget(object):
    """Hold information about ``plone.autoform.widgets.ParameterizedWidget``
    instances set via ``plone.autoform.directives.widget`` directive on schema
    fields. This information gets set on ``Field`` instances to gain information
    about the ``z3c.form`` widget used for this field.

    ``plone.autoform.directives.widget`` directive is not desired on schemata
    dedicated to yafowil forms, but used to interpret ``z3c.form`` related
    schemata with ``yafowil.plone.autoform``.
    """

    def __init__(self, factory, params):
        """Create widget.

        :param factory: ``ParameterizedWidget.widget_factory`` value.
        :param params: ``ParameterizedWidget.params`` value.
        """
        self.factory = factory
        self.params = params


def resolve_fieldset(schema):
    pass



def _resolve_schemata(schemata):
    # fieldset definitions
    fieldsets = dict()
    # field definitions
    fields = dict()
    # create default fieldset, not resolved by plone.autoform
    fieldsets['default'] = _FieldSet(
        'default',
        label=_('default', default='Default')
    )
    for idx, schema in enumerate(schemata):
        # assume first schema in list is main schema, all remaining are
        # behavior schemata
        is_behavior = idx != 0
        # collect all fieldsets from schema
        consumed_fields = set()
        schema_fieldsets = mergedTaggedValueList(schema, FIELDSETS_KEY)
        for schema_fieldset in schema_fieldsets:
            name = schema_fieldset.__name__
            label = schema_fieldset.label
            description = ''
            if schema_fieldset.description is not None:
                description = schema_fieldset.description
            order = DEFAULT_ORDER
            if schema_fieldset.order != DEFAULT_ORDER:
                fieldset.order = schema_fieldset.order
            fieldset = fieldsets.setdefault(
                name,
                _FieldSet(
                    name,
                    label=label,
                    description=description,
                    order=order
                )
            )
            if (
                schema_fieldset.label != fieldset.label and
                schema_fieldset.label != fieldset.__name__
            ):
                fieldset.label = schema_fieldset.label
            for field_name in schema_fieldset.fields:
                fieldset.fields.append(field_name)
                consumed_fields.add(field_name)
    return sorted(fieldsets.values(), key=attrgetter('order'))


###############################################################################
# prototype
###############################################################################

# field definition
Field = namedtuple(
    'Field',
    ['name', 'schemafield', 'schema', 'widget', 'mode', 'is_behavior']
)


# widget definition
Widget = namedtuple('Widget', ['factory', 'params'])


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
        label='Default'  # XXX: i18n
    )
    for idx, schema in enumerate(schemata):
        # assume first schema in list is main schema, all remaining are
        # behavior schemata
        is_behavior = idx != 0
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
        # collect annotated widgets for schema
        widgets = mergedTaggedValueDict(schema, WIDGETS_KEY)
        # collect all fields from schema and add field to return value and
        # fieldname to default fieldset if not already consumed
        for name, schemafield in getFieldsInOrder(schema):
            widget = widgets.get(name)
            if widget:
                # it seems that widget is always an instance of
                # ParameterizedWidget raise if not
                if not isinstance(widget, ParameterizedWidget):
                    raise RuntimeError('Unknown widget: {0}'.format(widget))
                # turn parametrized widget to namedtuple
                widget = Widget(
                    factory=widget.widget_factory,
                    params=widget.params
                )
            fields[name] = Field(
                name=name,
                schemafield=schemafield,
                schema=schema,
                widget=widget,
                mode='edit',  # XXX
                is_behavior=is_behavior
            )
            if name not in consumed_fields:
                fieldsets['default'].fields.append(name)
    return {
        'fieldsets': fieldsets,
        'fields': fields,
    }
