# -*- coding: utf-8 -*-
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.interface import implementer


class IImmediateAddedEvent(IObjectEvent):
    """After the object was created immediately, we want to fire an event."""


@implementer(IImmediateAddedEvent)
class ImmediateAddedEvent(ObjectEvent):
    """After the object was created immediately, we want to fire an event."""
