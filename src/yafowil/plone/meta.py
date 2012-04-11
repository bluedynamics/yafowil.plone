from zope.interface import Interface
from zope.browserresource.metaconfigure import allowed_names
from Products.Five.browser.metaconfigure import resourceDirectory
from yafowil.utils import (
    get_resource_directory,
    get_plugin_names,
)


class IYAFOWILResourceDirective(Interface):
    """Loader for plugin resources.
    """


def yafowil_resource_directive(_context):
    for module_name in get_plugin_names('resourcedir'):
        res_dir = get_resource_directory(module_name)
        resourceDirectory(_context, module_name, res_dir)