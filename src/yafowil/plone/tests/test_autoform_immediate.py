# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from yafowil.plone.autoform.events import ImmediateAddedEvent
from yafowil.plone.testing import YAFOWIL_PLONE_INTEGRATION_TESTING
from zope.component import getGlobalSiteManager

import unittest


class TestAdding(unittest.TestCase):
    """Test that collective.immediatecreate adding traverse and view creates.
    """

    layer = YAFOWIL_PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        fti = self.portal.portal_types.Folder
        behaviors = list(fti.getProperty("behaviors"))
        behaviors.append("yafowil.autoform.immediatecreate")
        fti._updateProperty("behaviors", behaviors)

    def test_unauthorized(self):
        view = self.portal.restrictedTraverse("++add++Folder")
        from zExceptions import Unauthorized

        self.assertRaises(Unauthorized, view)

    def test_creation_redirect(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor", "Editor"])
        view = self.portal.restrictedTraverse("++add++Folder")
        view()
        self.assertIn("location", view.request.response.headers)
        self.assertIn("new-folder", view.request.response.headers["location"])

    def test_creation_content(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor", "Editor"])
        view = self.portal.restrictedTraverse("++add++Folder")
        view()
        self.assertIn("new-folder", self.portal.contentIds())

    def test_creation_behavior(self):
        setRoles(self.portal, TEST_USER_ID, ["Contributor", "Editor"])
        view = self.portal.restrictedTraverse("++add++Folder")
        view()
        self.assertEqual(
            self.portal["new-folder"].yafowil_immediatecreate, "initial"
        )

    def test_event_handler(self):
        sm = getGlobalSiteManager()
        firedEvents = []

        def recordEvent(event):
            firedEvents.append(event.__class__)

        sm.registerHandler(recordEvent, (ImmediateAddedEvent,))

        setRoles(self.portal, TEST_USER_ID, ["Contributor", "Editor"])
        view = self.portal.restrictedTraverse("++add++Folder")
        view()

        self.assertListEqual(firedEvents, [ImmediateAddedEvent])
