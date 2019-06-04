from yafowil.base import factory
from yafowil.plone.connectors import plone_preprocessor

import os


###############################################################################
# plone5 specific resources
###############################################################################

resourcedir = os.path.join(os.path.dirname(__file__), 'resources', 'plone5')
css = [{
    'group': 'yafowil.plone.common',
    'resource': 'yafowil-fontello.css',
    'order': 10,
}, {
    'group': 'yafowil.plone.jqueryui',
    'resource': 'jqueryui/jquery-ui-1.10.3.custom.css',
    'order': 10,
}]

js = [{
    'group': 'yafowil.plone.jqueryui',
    'resource': 'jquery.migrate-1.2.1.min.js',
    'order': 5,
}, {
    'group': 'yafowil.plone.jqueryui',
    'resource': 'jqueryui/jquery-ui-1.10.3.custom.min.js',
    'order': 10,
}, {
    'group': 'yafowil.plone.common',
    'resource': 'widgets.js',
    'order': 30,
}]


###############################################################################
# configure factory
###############################################################################

def configure_factory():
    # set theme
    factory.theme = 'plone5'
    # selection
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
        'error.message_class': 'error',
        'error.render_empty': True,
        'error.position': 'before',
    })
    factory.register_macro('button', 'field:submit', {
        'field.class': 'formControls',
        'submit.class': 'context',
    })
    factory.register_macro('array', 'array', {})
    factory.register_macro('arrayfield', 'field:plonelabel:error', {})
    factory.register_macro('arrayrelation', 'relation', {
        'relation.pattern_name': 'array-relateditems'
    })


###############################################################################
# entry points
###############################################################################

def register():
    from yafowil.plone import widgets  # noqa: E501
    factory.register_global_preprocessors([plone_preprocessor])
    factory.register_theme('plone5', 'yafowil.plone', resourcedir, css=css, js=js)


def configure():
    configure_factory()
    register_macros()