from yafowil.base import factory
from yafowil.plone.connectors import plone_preprocessor
from zope.component import getUtility
from zope.component.hooks import getSite
import pkg_resources


###############################################################################
# Plone TinyMCE hook
###############################################################################

HAS_TINYMCE = True
try:
    pkg_resources.get_distribution('Products.TinyMCE')
    from Products.TinyMCE.interfaces.utility import ITinyMCE
except pkg_resources.DistributionNotFound:
    HAS_TINYMCE = False


def tinymce_config(widget, data):
    request = data.request.zrequest
    path = request.physicalPathFromURL(request.getURL())
    context = getSite()
    # query object by path, if not found, context is site
    for i in range(1, len(path)):
        brains = context.portal_catalog(path={
            'query': '/'.join(path[:-(i)]),
            'depth': 0})
        if not brains:
            continue
        context = brains[0].getObject()
        break
    utility = getUtility(ITinyMCE)
    config = utility.getConfiguration(context=context, request=request)
    return config.replace('"', '&#34;')


###############################################################################
# configure factory
###############################################################################

def configure_factory():
    # set theme
    factory.theme = 'plone4'
    # selection
    factory.defaults['select.label_radio_class'] = 'radioType'
    factory.defaults['select.label_checkbox_class'] = 'checkboxType'
    # tinymce
    if HAS_TINYMCE:
        factory.defaults['richtext.title'] = tinymce_config


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
    from yafowil.plone.widgets import label
    factory.register_global_preprocessors([plone_preprocessor])


def configure():
    configure_factory()
    register_macros()
