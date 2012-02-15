from zope.component import provideAdapter
from zope.security.checker import (
    CheckerPublic, 
    NamesChecker, 
    Checker,
)
from zope.browserresource.directory import DirectoryResourceFactory
from zope.browserresource.metaconfigure import allowed_names
from yafowil.utils import (
    get_resource_directory,
    get_plugin_names,
)
from yafowil.base import factory
from .connectors import zope2_preprocessor

# browser resource registration
allowed_names_dir =  allowed_names + ('__getitem__', 'get')
import pdb;pdb.set_trace()  
for module_name in get_plugin_names('resourcedir'):
    res_dir = get_resource_directory(module_name)
    
    checker = NamesChecker(allowed_names_dir, CheckerPublic)
    res_factory = DirectoryResourceFactory(res_dir, checker, module_name)
    provideAdapter(res_factory, adapts=IBrowserRequest, provides=None)

def register():
    factory.register_global_preprocessors([zope2_preprocessor])  
    

        