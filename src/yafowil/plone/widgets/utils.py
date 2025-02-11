from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from yafowil.utils import attr_value


def context_value(widget, data):
    """Lookup context value from widget attrs. Cannot use `attr_value`
    directly, because context itself is callable which we need to avoid.
    """
    context = widget.attrs['context']
    if isinstance(context, BrowserDefaultMixin):
        return context
    return attr_value("context", widget, data)
