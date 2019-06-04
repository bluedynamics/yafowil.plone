from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.content import Container
from plone.dexterity.fti import DexterityFTI
from yafowil.plone.autoform.behavior import IYafowilFormBehavior
from yafowil.plone.autoform.form import DefaultAddView
from yafowil.plone.testing import YAFOWIL_PLONE_INTEGRATION_TESTING
from zope.publisher.browser import TestRequest as TestRequestBase

import unittest


class TestRequest(TestRequestBase):
    """Zope 3's TestRequest doesn't support item assignment, but Zope 2's
    request does.
    """

    def __setitem__(self, key, value):
        pass


class TestAutoformForm(unittest.TestCase):
    layer = YAFOWIL_PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

    def test_default_add_view(self):
        context = Container(u"container")
        request = TestRequest()
        fti = DexterityFTI(u"testtype")
        addview = DefaultAddView(context, request, fti)
        self.assertFalse(addview.is_yafowil_form)

        fti.behaviors = (IYafowilFormBehavior.__identifier__,)
        addview = DefaultAddView(context, request, fti)
        self.assertTrue(addview.is_yafowil_form)
