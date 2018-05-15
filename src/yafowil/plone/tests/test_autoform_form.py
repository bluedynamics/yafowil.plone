from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from yafowil.plone.testing import YAFOWIL_PLONE_INTEGRATION_TESTING
import unittest


class TestAutoformForm(unittest.TestCase):
    layer = YAFOWIL_PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])

    def test_foo(self):
        self.assertEqual(1, 1)