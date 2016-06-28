from Products.Five.browser.metaconfigure import resourceDirectory
from yafowil.base import factory
from yafowil.utils import get_plugin_names
from zope.interface import Interface


class IYAFOWILResourceDirective(Interface):
    """Loader for plugin resources.
    """


def yafowil_resource_directive(_context):
    """Register plugin resource directories as plone resource directories
    to be accessible via browser URL.
    """
    for plugin_name in get_plugin_names():
        resources = factory.resources_for(plugin_name)
        if not resources:
            continue
        resourceDirectory(_context, plugin_name, resources['resourcedir'])
