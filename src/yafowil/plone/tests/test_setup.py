from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from yafowil.plone.testing import YAFOWIL_PLONE_INTEGRATION_TESTING
import unittest


class TestSetup(unittest.TestCase):
    """Test that yafowil.plone is properly installed.
    """
    layer = YAFOWIL_PLONE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests.
        """
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if yafowil.plone is installed.
        """
        self.assertTrue(self.installer.isProductInstalled('yafowil.plone'))

    def test_browserlayer(self):
        """Test that IYafowilLayer is registered.
        """
        from yafowil.plone.interfaces import IYafowilLayer
        from plone.browserlayer import utils
        self.assertIn(IYafowilLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):
    """Test that yafowil.plone is properly uninstalled.
    """
    layer = YAFOWIL_PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get(userid=TEST_USER_ID).getRoles()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['yafowil.plone'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if yafowil.plone is cleanly uninstalled.
        """
        self.assertFalse(self.installer.isProductInstalled('yafowil.plone'))

    def test_browserlayer_removed(self):
        """Test that IYafowilLayer is removed.
        """
        from yafowil.plone.interfaces import IYafowilLayer
        from plone.browserlayer import utils
        self.assertNotIn(IYafowilLayer, utils.registered_layers())
