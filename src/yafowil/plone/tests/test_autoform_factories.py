from node.utils import UNSET
from plone.app.contenttypes.interfaces import ILink
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.app.z3cform.widget import RichTextFieldWidget
from plone.autoform import directives as form
from plone.dexterity.interfaces import IDexterityFTI
from plone.supermodel import model
from yafowil.plone.autoform import FORM_SCOPE_ADD
from yafowil.plone.autoform import FORM_SCOPE_EDIT
from yafowil.plone.autoform import FORM_SCOPE_HOSTILE_ATTR
from yafowil.plone.autoform import factories
from yafowil.plone.autoform.factories import value_or_default
from yafowil.plone.autoform.factories import widget_factory
from yafowil.plone.autoform.schema import Field
from yafowil.plone.autoform.schema import Widget
from yafowil.plone.testing import YAFOWIL_PLONE_INTEGRATION_TESTING
from zope.component import queryUtility
from zope.interface import provider
from zope.schema import Text
from zope.schema import TextLine
from zope.schema.interfaces import IContextAwareDefaultFactory
import unittest


class TestAutoformFactories(unittest.TestCase):
    layer = YAFOWIL_PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

    def test_dedicated_field_widget_factory(self):
        class IDedicatedFieldSchema(model.Schema):
            field = TextLine(title=u'Dedicated field')

        @widget_factory(IDedicatedFieldSchema['field'])
        def dedicated_field_widget_factory(context, field):
            pass

        field = Field(
            name='field',
            schema=IDedicatedFieldSchema)
        factory = widget_factory._lookup_factory(field)
        self.assertEqual(factory, dedicated_field_widget_factory)

        del widget_factory._registry[IDedicatedFieldSchema['field']]

    def test_widget_bound_widget_factory(self):
        class IWidgetBoundFieldSchema(model.Schema):
            field = Text(title=u'Widget bound field')
            form.widget(field=RichTextFieldWidget)

        field = Field(
            name='field',
            schema=IWidgetBoundFieldSchema,
            widget=Widget(factory=RichTextFieldWidget, params={}))
        factory = widget_factory._lookup_factory(field)
        self.assertEqual(factory, factories.rich_text_field_widget_factory)

    def test_field_class_bound_widget_factory(self):
        class IFieldClassBoundFieldSchema(model.Schema):
            field = Text(title=u'Field class bound field')

        field = Field(
            name='field',
            schema=IFieldClassBoundFieldSchema)
        factory = widget_factory._lookup_factory(field)
        self.assertEqual(factory, factories.text_widget_factory)

    def test_value_or_default_no_scope(self):
        class IUnboundScopeSchema(model.Schema):
            field = TextLine(title=u'Unbound scope field')

        field = Field(
            name='field',
            schema=IUnboundScopeSchema)
        self.assertEqual(value_or_default(self.portal, field), UNSET)

    def test_value_or_default_scope_add(self):
        def field_1_default_value():
            return 'default 1'

        @provider(IContextAwareDefaultFactory)
        def field_2_default_value(container):
            return 'default 2'

        class IAddScopeSchema(model.Schema):
            field_1 = TextLine(
                title=u'Add scope field 1',
                defaultFactory=field_1_default_value)
            field_2 = TextLine(
                title=u'Add scope field 2',
                defaultFactory=field_2_default_value)
            field_3 = TextLine(title=u'Add scope field 3')

        setattr(self.request, FORM_SCOPE_HOSTILE_ATTR, FORM_SCOPE_ADD)

        field_1 = Field(
            name='field_1',
            schema=IAddScopeSchema)
        self.assertEqual(value_or_default(self.portal, field_1), 'default 1')

        field_2 = Field(
            name='field_2',
            schema=IAddScopeSchema)
        self.assertEqual(value_or_default(self.portal, field_2), 'default 2')

        field_3 = Field(
            name='field_3',
            schema=IAddScopeSchema)
        self.assertEqual(value_or_default(self.portal, field_3), UNSET)

        delattr(self.request, FORM_SCOPE_HOSTILE_ATTR)

    def test_value_or_default_scope_edit(self):
        self.portal.invokeFactory('Link', 'link')
        link = self.portal['link']
        link.remoteUrl = 'http://example.com'
        IExcludeFromNavigation(link).exclude_from_nav = True

        setattr(self.request, FORM_SCOPE_HOSTILE_ATTR, FORM_SCOPE_EDIT)

        fti = queryUtility(
            IDexterityFTI,
            name='Link')
        schema = fti.lookupSchema()

        remote_url = Field(
            name='remoteUrl',
            schema=schema)
        self.assertEqual(value_or_default(link, remote_url), 'http://example.com')

        exclude_from_nav = Field(
            name='exclude_from_nav',
            schema=IExcludeFromNavigation)
        self.assertEqual(value_or_default(link, exclude_from_nav), True)

        delattr(self.request, FORM_SCOPE_HOSTILE_ATTR)
