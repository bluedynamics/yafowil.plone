from plone.supermodel import model
from yafowil.plone.autoform.schema import _resolve_schemata
from zope.schema import TextLine
import unittest


###############################################################################
# mock objects
###############################################################################

class IBasicModel(model.Schema):

    field = TextLine(
        title=u'Text line',
        description=u'Text line description',
    )



###############################################################################
# tests
###############################################################################

class TestAutoformSchema(unittest.TestCase):

    def test_resolve_schemata(self):
        fieldsets = _resolve_schemata([IBasicModel])
        self.assertEqual(len(fieldsets), 1)
