from collections import namedtuple
from plone.autoform.interfaces import WIDGETS_KEY
from plone.autoform.utils import mergedTaggedValueDict
from plone.autoform.utils import mergedTaggedValueList
from plone.autoform.widgets import ParameterizedWidget
from plone.supermodel.interfaces import DEFAULT_ORDER
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from zope.schema import getFieldsInOrder


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
