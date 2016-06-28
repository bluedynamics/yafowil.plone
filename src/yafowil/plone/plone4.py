from yafowil.base import factory
from yafowil.plone.connectors import plone_preprocessor


###############################################################################
# configure factory
###############################################################################

def configure_factory():
    factory.defaults['select.label_radio_class'] = 'radioType'
    factory.defaults['select.label_checkbox_class'] = 'checkboxType'


###############################################################################
# register macros
###############################################################################

def register_macros():
    factory.register_macro('form', 'form', {
        'form.class': 'enableUnloadProtection enableAutoFocus '
                      'enableFormTabbing edit-form',
    })
    factory.register_macro('field', 'field:plonelabel:error', {
        'field.class': 'field',
        'field.error_class': 'error',
        'error.class': 'fieldErrorBox',
        'error.render_empty': True,
        'error.position': 'before',
    })
    factory.register_macro('button', 'field:submit', {
        'field.class': 'formControls',
        'submit.class': 'context',
    })
    factory.register_macro('array', 'array', {})
    factory.register_macro('arrayfield', 'field:plonelabel:error', {})


###############################################################################
# entry points
###############################################################################

def register():
    import common
    factory.register_global_preprocessors([plone_preprocessor])


def configure():
    configure_factory()
    register_macros()
