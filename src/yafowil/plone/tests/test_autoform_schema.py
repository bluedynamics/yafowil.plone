from plone.supermodel import model
from yafowil.plone.autoform.schema import resolve_schemata
from yafowil.plone.autoform.schema import Fieldset
from yafowil.plone.autoform.schema import Field
from yafowil.plone.autoform.schema import Widget
from zope.schema import TextLine
from zope.schema import getFieldsInOrder
import unittest


###############################################################################
# mock objects
###############################################################################

class IBasicModel(model.Schema):
    field = TextLine(
        title=u'Basic field',
        description=u'Basic field description')


class IBehavior1(model.Schema):
    field = TextLine(
        title=u'Behavior 1 field',
        description=u'Behavior1 field description')


class IBehavior2(model.Schema):
    other = TextLine(
        title=u'Behavior 2 other',
        description=u'Behavior 2 other description')


class IFieldsetModel(model.Schema):
    model.fieldset('fieldset', fields=['field2'])
    field1 = TextLine(title=u'Default model field')
    field2 = TextLine(title=u'Fieldset model field')


class IFieldsetBehavior(model.Schema):
    model.fieldset('fieldset', label=u'Fieldset', fields=['field2'])
    field1 = TextLine(title=u'Default behavior field')
    field2 = TextLine(title=u'Fieldset behavior field')


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

        fieldname, schemafield = getFieldsInOrder(IBasicModel)[0]
        field = Field(
            name=fieldname,
            schemafield=schemafield,
            schema=IBasicModel,
            widget=None,
            mode='edit',
            is_behavior=False)
        fieldset.add(field)
        self.assertEqual(list(fieldset.__iter__()), [field])
        self.assertEqual(fieldset.children, [field])

    def test_Field(self):
        fieldname, schemafield = getFieldsInOrder(IBasicModel)[0]
        field = Field(
            name=fieldname,
            schemafield=schemafield,
            schema=IBasicModel,
            widget=None,
            mode='edit',
            is_behavior=False)
        self.assertEqual(field.name, fieldname)
        self.assertEqual(field.schemafield, schemafield)
        self.assertEqual(field.schema, IBasicModel)
        self.assertEqual(field.widget, None)
        self.assertEqual(field.mode, 'edit')
        self.assertEqual(field.is_behavior, False)
        self.assertEqual(field.label, 'Basic field')
        self.assertEqual(field.help, 'Basic field description')

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

        field = next(fieldset.__iter__())
        self.assertEqual(field.name, 'field')
        self.assertEqual(field.schema, IBasicModel)
        self.assertEqual(field.label, 'Basic field')
        self.assertEqual(field.is_behavior, False)

    def test_resolve_schemata_basic_and_behaviors(self):
        fieldsets = resolve_schemata([IBasicModel, IBehavior1, IBehavior2])
        self.assertEqual(len(fieldsets), 1)

        fieldset = fieldsets[0]
        self.assertEqual(len(fieldset.children), 3)
        self.assertEqual(fieldset.name, 'default')

        field = fieldset.children[0]
        self.assertEqual(field.name, 'field')
        self.assertEqual(field.schema, IBasicModel)
        self.assertEqual(field.label, 'Basic field')
        self.assertEqual(field.is_behavior, False)

        field = fieldset.children[1]
        self.assertEqual(field.name, 'field')
        self.assertEqual(field.schema, IBehavior1)
        self.assertEqual(field.label, 'Behavior 1 field')
        self.assertEqual(field.is_behavior, True)

        field = fieldset.children[2]
        self.assertEqual(field.name, 'other')
        self.assertEqual(field.schema, IBehavior2)
        self.assertEqual(field.label, 'Behavior 2 other')
        self.assertEqual(field.is_behavior, True)

    def test_resolve_schemata_fieldsets(self):
        fieldsets = resolve_schemata([IFieldsetModel, IFieldsetBehavior])
        self.assertEqual(len(fieldsets), 2)

        fieldset = fieldsets[0]
        self.assertEqual(fieldset.name, 'default')
        self.assertEqual(len(fieldset.children), 2)

        field = fieldset.children[0]
        self.assertEqual(field.name, 'field1')
        self.assertEqual(field.schema, IFieldsetModel)
        self.assertEqual(field.is_behavior, False)

        field = fieldset.children[1]
        self.assertEqual(field.name, 'field1')
        self.assertEqual(field.schema, IFieldsetBehavior)
        self.assertEqual(field.is_behavior, True)

        fieldset = fieldsets[1]
        self.assertEqual(fieldset.name, 'fieldset')
        self.assertEqual(len(fieldset.children), 2)

        field = fieldset.children[0]
        self.assertEqual(field.name, 'field2')
        self.assertEqual(field.schema, IFieldsetModel)
        self.assertEqual(field.is_behavior, False)

        field = fieldset.children[1]
        self.assertEqual(field.name, 'field2')
        self.assertEqual(field.schema, IFieldsetBehavior)
        self.assertEqual(field.is_behavior, True)
