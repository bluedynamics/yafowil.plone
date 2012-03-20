from yafowil.base import factory
from .connectors import zope2_preprocessor

def register():
    factory.register_global_preprocessors([zope2_preprocessor])  
    factory.defaults['form.class'] = 'edit-form enableUnloadProtection enableAutoFocus'    
    factory.defaults['label.class'] = "formQuestion"