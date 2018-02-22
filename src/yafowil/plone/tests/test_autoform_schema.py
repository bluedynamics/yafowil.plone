from plone.supermodel import model
from yafowil.plone.autoform.schema import _resolve_schemata
from yafowil.plone.autoform.schema import _Fieldset
from yafowil.plone.autoform.schema import _Field
from yafowil.plone.autoform.schema import _Widget
from zope.schema import TextLine
from zope.schema import getFieldsInOrder
import unittest


###############################################################################
# mock objects
###############################################################################

class IBasicModel(model.Schema):

    field = TextLine(
        title=u'Basic field',
        description=u'Basic field description',
    )


class IBehavior1(model.Schema):

    field = TextLine(
        title=u'Behavior 1 field',
        description=u'Behavior1 field description',
    )


class IBehavior2(model.Schema):

    other = TextLine(
        title=u'Behavior 2 other',
        description=u'Behavior 2 other description',
    )


###############################################################################
# tests
###############################################################################

class TestAutoformSchema(unittest.TestCase):

    def test_Fieldset(self):
        fieldset = _Fieldset(
            name='default',
            label='Default',
            description='Default fieldset',
            order=0
        )
        self.assertEqual(fieldset.name, 'default')
        self.assertEqual(fieldset.label, 'Default')
        self.assertEqual(fieldset.description, 'Default fieldset')
        self.assertEqual(fieldset.order, 0)

        fieldname, schemafield = getFieldsInOrder(IBasicModel)[0]
        field = _Field(
            name=fieldname,
            schemafield=schemafield,
            schema=IBasicModel,
            widget=None,
            mode='edit',
            is_behavior=False
        )
        fieldset.add(field)
        self.assertEqual(list(fieldset.__iter__()), [field])
        self.assertEqual(fieldset.children, [field])

    def test_Field(self):
        fieldname, schemafield = getFieldsInOrder(IBasicModel)[0]
        field = _Field(
            name=fieldname,
            schemafield=schemafield,
            schema=IBasicModel,
            widget=None,
            mode='edit',
            is_behavior=False
        )
        self.assertEqual(field.name, fieldname)
        self.assertEqual(field.schemafield, schemafield)
        self.assertEqual(field.schema, IBasicModel)
        self.assertEqual(field.widget, None)
        self.assertEqual(field.mode, 'edit')
        self.assertEqual(field.is_behavior, False)
        self.assertEqual(field.label, 'Basic field')
        self.assertEqual(field.help, 'Basic field description')

    def test_Widget(self):
        widget = _Widget(factory=None, params={'foo': 'bar'})
        self.assertEqual(widget.factory, None)
        self.assertEqual(widget.params, {'foo': 'bar'})

    def test_resolve_schemata_basic(self):
        fieldsets = _resolve_schemata([IBasicModel])
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
        fieldsets = _resolve_schemata([IBasicModel, IBehavior1, IBehavior2])
        self.assertEqual(len(fieldsets), 1)

        fieldset = fieldsets[0]
        self.assertEqual(len(fieldset.children), 3)

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
