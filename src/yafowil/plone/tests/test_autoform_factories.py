from yafowil.plone.testing import YAFOWIL_PLONE_INTEGRATION_TESTING
import unittest


class TestAutoformFactories(unittest.TestCase):
    layer = YAFOWIL_PLONE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests.
        """
        self.portal = self.layer['portal']

    def test_dummy(self):
        pass
