# -*- coding: utf-8 -*-
from yafowil.plone.testing import YAFOWIL_PLONE_INTEGRATION_TESTING
from plone.supermodel import model
from zope.schema import TextLine

import unittest


class TestAutoformDirectives(unittest.TestCase):

    layer = YAFOWIL_PLONE_INTEGRATION_TESTING

    def test_schema_directives_store_tagged_values(self):

        from yafowil.plone.autoform import directives

        class IDummy(model.Schema):

            directives.factory(
                'foo',
                blueprints='#field:*my:text',
                value='FOO',
                props={},
                custom={},
                mode='edit',
            )
            foo = TextLine(title=u'Foo')

            directives.factory(
                'bar',
                blueprints='#field:*my:text',
            )
            directives.order('bar', before='foo')
            bar = TextLine(title=u'Bar')

            directives.order('baz', after='qux')
            baz = TextLine(title=u'Baz')

            qux = TextLine(title=u'Qux')

            directives.modifier('modifier_1')

            directives.order('qix', fieldset='other')
            qix = TextLine(title=u'Qix')

            directives.modifier('modifier_2')
            directives.modifier('modifier_3')

        self.assertEqual(
            IDummy.queryTaggedValue(directives.FACTORY_KEY),
            {
                'bar': {'blueprints': '#field:*my:text'},
                'foo': {
                    'blueprints': '#field:*my:text',
                    'custom': {},
                    'mode': 'edit',
                    'props': {},
                    'value': 'FOO',
                },
            }
        )
        self.assertEqual(
            IDummy.queryTaggedValue(directives.ORDER_KEY),
            {
                'bar': {'after': None, 'before': 'foo', 'fieldset': None},
                'baz': {'after': 'qux', 'before': None, 'fieldset': None},
                'qix': {'after': None, 'before': None, 'fieldset': 'other'},
            },
        )
        self.assertEqual(
            IDummy.queryTaggedValue(directives.MODIFER_KEY),
            ['modifier_1', 'modifier_2', 'modifier_3'],
        )
