from plone.app.z3cform.widget import RichTextFieldWidget
from plone.autoform import directives as form
from plone.supermodel import model
from yafowil.plone.autoform import factories
from yafowil.plone.autoform.factories import widget_factory
from yafowil.plone.autoform.schema import Field
from yafowil.plone.autoform.schema import Widget
from yafowil.plone.testing import YAFOWIL_PLONE_INTEGRATION_TESTING
from zope.schema import Text
from zope.schema import TextLine
import unittest


class TestAutoformFactories(unittest.TestCase):
    layer = YAFOWIL_PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_dedicated_field_widget_factory(self):
        class IDedicatedFieldSchema(model.Schema):
            field = TextLine(title=u'Dedicated field')

        @widget_factory(IDedicatedFieldSchema['field'])
        def dedicated_field_widget_factory(context, field):
            pass

        field = Field(
            name='field',
            schemafield=IDedicatedFieldSchema['field'],
            schema=IDedicatedFieldSchema,
            widget=None,
            mode='edit',
            is_behavior=False
        )
        factory = widget_factory._lookup_factory(field)
        self.assertEqual(factory, dedicated_field_widget_factory)

        del widget_factory._registry[IDedicatedFieldSchema['field']]

    def test_widget_bound_widget_factory(self):
        class IWidgetBoundFieldSchema(model.Schema):
            field = Text(title=u'Widget bound field')
            form.widget(field=RichTextFieldWidget)

        field = Field(
            name='field',
            schemafield=IWidgetBoundFieldSchema['field'],
            schema=IWidgetBoundFieldSchema,
            widget=Widget(factory=RichTextFieldWidget, params={}),
            mode='edit',
            is_behavior=False
        )
        factory = widget_factory._lookup_factory(field)
        self.assertEqual(factory, factories.rich_text_field_widget_factory)

    def test_field_class_bound_widget_factory(self):
        class IFieldClassBoundFieldSchema(model.Schema):
            field = Text(title=u'Field class bound field')

        field = Field(
            name='field',
            schemafield=IFieldClassBoundFieldSchema['field'],
            schema=IFieldClassBoundFieldSchema,
            widget=None,
            mode='edit',
            is_behavior=False
        )
        factory = widget_factory._lookup_factory(field)
        self.assertEqual(factory, factories.text_widget_factory)
