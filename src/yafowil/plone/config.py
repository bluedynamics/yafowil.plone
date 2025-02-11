from yafowil.base import factory
from yafowil.bootstrap import configure_factory
from yafowil.plone.connectors import plone_preprocessor
from yafowil.plone.resources import resources


###############################################################################
# register macros
###############################################################################

def configure_defaults():
    # yafowil.widget.ace
    factory.defaults['ace.basepath'] = '/++resource++yafowil.widget.ace/ace'


###############################################################################
# register macros
###############################################################################

def register_macros():
    # form macro
    factory.register_macro('form', 'form', {
        'form.class_add': (
            'enableUnloadProtection enableAutoFocus '
            'enableFormTabbing edit-form'
        ),
    })

    # field macro
    factory.register_macro('field', 'field:plonelabel:error', {
        'field.class_add': 'field mb-3',
    })

    # array macro
    factory.register_macro('array', 'array', {})

    # array field macro
    factory.register_macro('arrayfield', 'field:plonelabel:error', {})

    # relation as array entry macro
    factory.register_macro('arrayrelation', 'relation', {
        'relation.pattern_name': 'array-relateditems'
    })

    # richtext as array entry macro
    factory.register_macro('arrayrichtext', 'plonerichtext', {
        'plonerichtext.mimetype_selector_class': 'plonearrayrichtext',
        'plonerichtext.pattern_name': 'array-textareamimetypeselector'
    })


###############################################################################
# entry points
###############################################################################

def register():
    from yafowil.plone import widgets  # noqa: E501
    factory.register_global_preprocessors([plone_preprocessor])
    factory.register_resources(['bootstrap5'], 'yafowil.plone', resources)


def configure():
    configure_factory('bootstrap5')
    configure_defaults()
    register_macros()
