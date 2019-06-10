from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IYafowilLayer(IDefaultBrowserLayer):
    """YAFOWIL related browser layer.
    """


class IYafowilDemoLayer(IYafowilLayer):
    """YAFOWIL demos related browser layer.
    """
