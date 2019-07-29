# -*- coding: utf-8 -*-
from plone.supermodel import model
from yafowil.base import factory
from yafowil.plone.autoform import directives
from yafowil.plone.testing import YAFOWIL_PLONE_INTEGRATION_TESTING
from zope.interface import Interface
from zope.schema import TextLine
import unittest


###############################################################################
# mock objects
###############################################################################

def dummy_factory_callable(context):
    return factory('text')


def dummy_modifier_1(context, form):
    pass


def dummy_modifier_2(context, form):
    pass


def dummy_modifier_3(context, form):
    pass


class IDummySchema(model.Schema):
    foo = TextLine(title=u'Foo')
    directives.factory(
        'foo',
        blueprints='#field:*my:text',
        value='FOO',
        props={},
        custom={},
        mode='edit',
    )

    bar = TextLine(title=u'Bar')
    directives.factory(
        'bar',
        blueprints='#field:*my:text',
    )
    directives.order('bar', before='foo')

    baz = TextLine(title=u'Baz')
    directives.order('baz', after='qux')

    qux = TextLine(title=u'Qux')
    directives.factory_callable('qux', dummy_factory_callable)

    directives.modifier(dummy_modifier_1)

    qix = TextLine(title=u'Qix')
    directives.order('qix', fieldset='other')

    directives.modifier(dummy_modifier_2)
    directives.modifier(dummy_modifier_3)


class IDummySchema2(model.Schema):
    foo = TextLine(title=u'Foo')


###############################################################################
# tests
###############################################################################

class TestAutoformDirectives(unittest.TestCase):
    layer = YAFOWIL_PLONE_INTEGRATION_TESTING
    maxDiff = None

    def test_factory_tagged_values(self):
        self.assertEqual(
            IDummySchema.queryTaggedValue(directives.FACTORY_KEY),
            {
                'bar': {'blueprints': '#field:*my:text'},
                'foo': {
                    'blueprints': '#field:*my:text',
                    'custom': {},
                    'mode': 'edit',
                    'props': {},
                    'value': 'FOO'
                }
            }
        )

    def test_factory_callable_tagged_values(self):
        self.assertEqual(
            IDummySchema.queryTaggedValue(directives.FACTORY_CALLABLE_KEY),
            {'qux': dummy_factory_callable}
        )

    def test_order_tagged_values(self):
        self.assertEqual(
            IDummySchema.queryTaggedValue(directives.ORDER_KEY),
            {
                'bar': {'after': None, 'before': 'foo', 'fieldset': None},
                'baz': {'after': 'qux', 'before': None, 'fieldset': None},
                'qix': {'after': None, 'before': None, 'fieldset': 'other'}
            }
        )

    def test_modifier_tagged_values(self):
        self.assertEqual(
            IDummySchema.queryTaggedValue(directives.MODIFIER_KEY),
            [dummy_modifier_1, dummy_modifier_2, dummy_modifier_3],
        )

    def test_tgv_cache_factory(self):
        cache = directives.tgv_cache
        self.assertEqual(cache._cache[directives.FACTORY_KEY], {})
        self.assertEqual(cache.get_factory(IDummySchema, 'inexistent'), None)
        self.assertEqual(cache._cache[directives.FACTORY_KEY], {
            IDummySchema: {
                'foo': {
                    'blueprints': '#field:*my:text',
                    'custom': {},
                    'mode': 'edit',
                    'value': 'FOO',
                    'props': {}
                },
                'bar': {'blueprints': '#field:*my:text'}
            },
            Interface: None,
            model.Schema: None
        })
        self.assertEqual(cache.get_factory(IDummySchema, 'bar'), {
            'blueprints': '#field:*my:text'
        })

    def test_tgv_cache_factory_callable(self):
        cache = directives.tgv_cache
        self.assertEqual(cache._cache[directives.FACTORY_CALLABLE_KEY], {})
        self.assertEqual(
            cache.get_factory_callable(IDummySchema, 'inexistent'),
            None
        )
        self.assertEqual(
            cache._cache[directives.FACTORY_CALLABLE_KEY],
            {
                IDummySchema: {'qux': dummy_factory_callable},
                Interface: None,
                model.Schema: None
            }
        )
        self.assertEqual(
            cache.get_factory_callable(IDummySchema, 'qux'),
            dummy_factory_callable
        )

    def test_tgv_cache_order(self):
        cache = directives.tgv_cache
        self.assertEqual(cache._cache[directives.ORDER_KEY], {})
        self.assertEqual(cache.get_order(IDummySchema, 'inexistent'), None)
        self.assertEqual(cache._cache[directives.ORDER_KEY], {
            IDummySchema: {
                'bar': {'after': None, 'before': 'foo', 'fieldset': None},
                'baz': {'after': 'qux', 'before': None, 'fieldset': None},
                'qix': {'after': None, 'before': None, 'fieldset': 'other'}
            },
            Interface: None,
            model.Schema: None
        })
        self.assertEqual(cache.get_order(IDummySchema, 'bar'), {
            'after': None,
            'before': 'foo',
            'fieldset': None
        })

    def test_tgv_cache_modifier(self):
        cache = directives.tgv_cache
        self.assertEqual(cache._cache[directives.MODIFIER_KEY], {})
        self.assertEqual(
            cache.get_modifier(IDummySchema),
            [dummy_modifier_1, dummy_modifier_2, dummy_modifier_3]
        )
        self.assertEqual(cache._cache[directives.MODIFIER_KEY], {
            IDummySchema: [dummy_modifier_1, dummy_modifier_2, dummy_modifier_3],
            Interface: None,
            model.Schema: None
        })
        self.assertEqual(cache.get_modifier(IDummySchema2), [])
        self.assertEqual(cache._cache[directives.MODIFIER_KEY], {
            IDummySchema: [dummy_modifier_1, dummy_modifier_2, dummy_modifier_3],
            IDummySchema2: None,
            Interface: None,
            model.Schema: None
        })

    def test_context_aware_callable(self):

        def cb(context, widget, data):
            return context, widget, data

        ctxawarecallable = directives.ContextAwareCallable('context', cb)
        self.assertEqual(
            ctxawarecallable('widget', 'data'),
            ('context', 'widget', 'data')
        )
