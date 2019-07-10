from plone.autoform import directives as form
from plone.supermodel import model
from yafowil.plone.autoform.schema import Field
from yafowil.plone.autoform.schema import Fieldset
from yafowil.plone.autoform.schema import resolve_schemata
from yafowil.plone.autoform.schema import Widget
from z3c.form.browser.text import TextWidget
from zope.schema import getFieldNamesInOrder
from zope.schema import TextLine

import unittest


###############################################################################
# mock objects
###############################################################################

class IBasicModel(model.Schema):
    field = TextLine(
        title=u'Basic field',
        description=u'Basic field description')


class IBehavior1(model.Schema):
    field = TextLine(title=u'Behavior 1 field')


class IBehavior2(model.Schema):
    other = TextLine(title=u'Behavior 2 other')


class IFieldsetModel(model.Schema):
    model.fieldset('fieldset', fields=['field2'])
    field1 = TextLine(title=u'Default model field')
    field2 = TextLine(title=u'Fieldset model field')


class IFieldsetBehavior(model.Schema):
    model.fieldset('fieldset', label=u'Fieldset', fields=['field2'])
    field1 = TextLine(title=u'Default behavior field')
    field2 = TextLine(title=u'Fieldset behavior field')


class IWidgetUsingModel(model.Schema):
    # For available options see ``plone.autoform.directives.widget`` docs.

    # Option 1
    field1 = TextLine(title=u'Field 1')
    field2 = TextLine(title=u'Field 2')
    form.widget(field1='z3c.form.browser.text.TextWidget', field2=TextWidget)

    # Option 2
    field3 = TextLine(title=u'Field 3')
    form.widget('field3', TextWidget, label=u'Label 3')

    # Option 3
    field4 = TextLine(title=u'Field 4')
    form.widget('field4', label=u'Label 4')


class IModeUsingModel(IBasicModel):
    form.mode(field='hidden')

    field1 = TextLine(title=u'Field 1')
    form.mode(field1='hidden')


class IOrderUsingMainSchema(model.Schema):
    field_m_1 = TextLine(title=u'Field m 1')
    field_m_2 = TextLine(title=u'Field m 2')


class IOrderUsingBehavior1(model.Schema):
    field_1_1 = TextLine(title=u'Field 1 1')
    form.order_before(field_1_1='field_m_1')

    field_1_2 = TextLine(title=u'Field 1 2')
    form.order_after(field_1_2='.field_1_1')


class IOrderUsingBehavior2(model.Schema):
    field_2_1 = TextLine(title=u'Field 2 1')
    form.order_after(field_2_1='IOrderUsingBehavior1.field_1_2')

    field_2_2 = TextLine(title=u'Field 2 2')
    form.order_before(field_2_2='*')


###############################################################################
# tests
###############################################################################

class TestAutoformSchema(unittest.TestCase):

    def test_Fieldset(self):
        fieldset = Fieldset(
            name='default',
            label='Default',
            description='Default fieldset',
            order=0)
        self.assertEqual(fieldset.name, 'default')
        self.assertEqual(fieldset.label, 'Default')
        self.assertEqual(fieldset.description, 'Default fieldset')
        self.assertEqual(fieldset.order, 0)

        fieldname = getFieldNamesInOrder(IBasicModel)[0]
        field = Field(
            name=fieldname,
            schema=IBasicModel)
        fieldset.add(field)
        self.assertEqual(list(fieldset.__iter__()), [field])
        self.assertEqual(fieldset.children, [field])

    def test_Field(self):
        fieldname = getFieldNamesInOrder(IBasicModel)[0]
        field = Field(
            name=fieldname,
            schema=IBasicModel)
        self.assertEqual(field.name, fieldname)
        self.assertEqual(field.schema, IBasicModel)
        self.assertEqual(field.widget, None)
        self.assertEqual(field.mode, 'edit')
        self.assertEqual(field.is_behavior, False)
        self.assertEqual(field.schemafield, IBasicModel[fieldname])
        self.assertEqual(field.label, 'Basic field')
        self.assertEqual(field.help, 'Basic field description')
        self.assertEqual(field.required, True)

    def test_Widget(self):
        widget = Widget(factory=None, params={'foo': 'bar'})
        self.assertEqual(widget.factory, None)
        self.assertEqual(widget.params, {'foo': 'bar'})

    def test_resolve_schemata_basic(self):
        fieldsets = resolve_schemata([IBasicModel])
        self.assertEqual(len(fieldsets), 1)

        fieldset = fieldsets[0]
        self.assertEqual(len(fieldset.children), 1)
        self.assertEqual(fieldset.name, 'default')
        self.assertEqual(fieldset.label, 'label_schema_default')

        field = next(fieldset.__iter__())
        self.assertEqual(field.name, 'field')
        self.assertEqual(field.schemafield, IBasicModel['field'])
        self.assertEqual(field.schema, IBasicModel)
        self.assertEqual(field.widget, None)
        self.assertEqual(field.mode, 'edit')
        self.assertEqual(field.is_behavior, False)
        self.assertEqual(field.label, 'Basic field')
        self.assertEqual(field.help, 'Basic field description')
        self.assertEqual(field.required, True)

    def test_resolve_schemata_basic_and_behaviors(self):
        fieldsets = resolve_schemata([IBasicModel, IBehavior1, IBehavior2])
        self.assertEqual(len(fieldsets), 1)

        fieldset = fieldsets[0]
        self.assertEqual(len(fieldset.children), 3)
        self.assertEqual(fieldset.name, 'default')

        field = fieldset.children[0]
        self.assertEqual(field.name, 'field')
        self.assertEqual(field.schema, IBasicModel)
        self.assertEqual(field.is_behavior, False)
        self.assertEqual(field.label, 'Basic field')

        field = fieldset.children[1]
        self.assertEqual(field.name, 'field')
        self.assertEqual(field.schema, IBehavior1)
        self.assertEqual(field.is_behavior, True)
        self.assertEqual(field.label, 'Behavior 1 field')

        field = fieldset.children[2]
        self.assertEqual(field.name, 'other')
        self.assertEqual(field.schema, IBehavior2)
        self.assertEqual(field.is_behavior, True)
        self.assertEqual(field.label, 'Behavior 2 other')

    def test_resolve_schemata_fieldsets(self):
        fieldsets = resolve_schemata([IFieldsetModel, IFieldsetBehavior])
        self.assertEqual(len(fieldsets), 2)

        fieldset = fieldsets[0]
        self.assertEqual(len(fieldset.children), 2)
        self.assertEqual(fieldset.name, 'default')

        field = fieldset.children[0]
        self.assertEqual(field.name, 'field1')
        self.assertEqual(field.schema, IFieldsetModel)
        self.assertEqual(field.label, 'Default model field')

        field = fieldset.children[1]
        self.assertEqual(field.name, 'field1')
        self.assertEqual(field.schema, IFieldsetBehavior)
        self.assertEqual(field.label, 'Default behavior field')

        fieldset = fieldsets[1]
        self.assertEqual(len(fieldset.children), 2)
        self.assertEqual(fieldset.name, 'fieldset')
        self.assertEqual(fieldset.label, 'Fieldset')

        field = fieldset.children[0]
        self.assertEqual(field.name, 'field2')
        self.assertEqual(field.schema, IFieldsetModel)
        self.assertEqual(field.label, 'Fieldset model field')

        field = fieldset.children[1]
        self.assertEqual(field.name, 'field2')
        self.assertEqual(field.schema, IFieldsetBehavior)
        self.assertEqual(field.label, 'Fieldset behavior field')

    def test_resolve_schemata_widgets(self):
        fieldsets = resolve_schemata([IWidgetUsingModel])
        self.assertEqual(len(fieldsets), 1)

        fieldset = fieldsets[0]
        self.assertEqual(len(fieldset.children), 4)
        self.assertEqual(fieldset.name, 'default')

        field = fieldset.children[0]
        self.assertEqual(field.name, 'field1')
        widget = field.widget
        self.assertEqual(widget.factory, TextWidget)
        self.assertEqual(widget.params, {})

        field = fieldset.children[1]
        self.assertEqual(field.name, 'field2')
        widget = field.widget
        self.assertEqual(widget.factory, TextWidget)
        self.assertEqual(widget.params, {})

        field = fieldset.children[2]
        self.assertEqual(field.name, 'field3')
        widget = field.widget
        self.assertEqual(widget.factory, TextWidget)
        self.assertEqual(widget.params, {'label': 'Label 3'})

        field = fieldset.children[3]
        self.assertEqual(field.name, 'field4')
        widget = field.widget
        self.assertEqual(widget.factory, None)
        self.assertEqual(widget.params, {'label': 'Label 4'})

    def test_resolve_schemata_field_modes(self):
        fieldsets = resolve_schemata([IModeUsingModel])
        self.assertEqual(len(fieldsets), 1)

        fieldset = fieldsets[0]
        self.assertEqual(len(fieldset.children), 2)
        self.assertEqual(fieldset.name, 'default')

        field = fieldset.children[0]
        self.assertEqual(field.name, 'field')
        self.assertEqual(field.mode, 'skip')

        field = fieldset.children[1]
        self.assertEqual(field.name, 'field1')
        self.assertEqual(field.mode, 'skip')

    def test_resolve_schemata_field_order(self):
        fieldsets = resolve_schemata([
            IOrderUsingMainSchema,
            IOrderUsingBehavior1,
            IOrderUsingBehavior2
        ])
        self.assertEqual(len(fieldsets), 1)

        fieldset = fieldsets[0]
        self.assertEqual(len(fieldset.children), 6)
        self.assertEqual(fieldset.name, 'default')

        self.assertEqual([field.name for field in fieldset.children], [
            'field_2_2',
            'field_1_1',
            'field_1_2',
            'field_2_1',
            'field_m_1',
            'field_m_2'
        ])
