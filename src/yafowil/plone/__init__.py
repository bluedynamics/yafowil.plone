from yafowil.base import factory
from .connectors import plone_preprocessor

PLONE_MACROS = {
    'form': {
        'chain': 'form',
        'props': {
            'form.class': 'enableUnloadProtection enableAutoFocus '
                          'enableFormTabbing edit-form',
        }
    },
    'field': {
        'chain': 'field:label:help:error',
        'props': {
            'field.class': 'field',
            'label.class': 'formQuestion',
            'help.class': 'formHelp',
            'error.class': 'fieldErrorBox',
            'error.render_empty': True,
            'error.position': 'before',
        }
    },
    'button': {
        'chain': 'field:submit',
        'props': {
            'field.class': 'formControls',
            'submit.class': 'context',
        }
    },
    
    # yafowil.widget.array
    'array': {
        'chain': 'array',
        'props': {},
    },
}


def register():
    factory.register_global_preprocessors([plone_preprocessor])
    for name, value in PLONE_MACROS.items():
        factory.register_macro(name, value['chain'], value['props'])
    factory.defaults['select.label_radio_class'] = 'radioType'
    factory.defaults['select.label_checkbox_class'] = 'checkboxType'
