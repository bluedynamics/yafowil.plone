# -*- coding: utf-8 -*-
from zope.interface import implementer
try:
    from zope.interface.interfaces import IObjectEvent
    from zope.interface.interfaces import ObjectEvent
except ImportError:
    # BBB
    from zope.component.interfaces import IObjectEvent
    from zope.component.interfaces import ObjectEvent


class IImmediateAddedEvent(IObjectEvent):
    """After the object was created immediately, we want to fire an event."""


@implementer(IImmediateAddedEvent)
class ImmediateAddedEvent(ObjectEvent):
    """After the object was created immediately, we want to fire an event."""
