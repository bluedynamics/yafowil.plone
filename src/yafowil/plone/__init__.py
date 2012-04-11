from yafowil.base import factory
from .connectors import plone_preprocessor


def register():
    factory.register_global_preprocessors([plone_preprocessor])  
    factory.defaults['form.class'] = \
        'edit-form enableUnloadProtection enableAutoFocus'    
    factory.defaults['label.class'] = "formQuestion"