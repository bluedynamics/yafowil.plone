from plone.supermodel import model
from zope.interface import Attribute


class IYafowilFormBehavior(model.Schema):
    """Behavior for replacing content CRUD forms with YAFOWIL implementation.

    Works on a temporary non-persistent add context.
    """


class IYafowilImmediateCreateBehavior(IYafowilFormBehavior):
    """Behavior for replacing content CRUD forms with YAFOWIL implementation.

    Creates immediately a pesistent context to work.
    """

    yafowil_immediatecreate = Attribute(u"Was this item initially saved?")
