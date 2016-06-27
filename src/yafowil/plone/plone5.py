from yafowil.base import factory
from yafowil.plone.connectors import plone_preprocessor
import os


###############################################################################
# Plone 5 specific resources
###############################################################################

resourcedir = os.path.join(os.path.dirname(__file__), 'plone5')
css = [{
    'group': 'bootstrap.glyphicons',
    'resource': 'glyphicons.css',
    'order': 10,
}]


###############################################################################
# configure factory
###############################################################################

def configure_factory():
    pass


###############################################################################
# register macros
###############################################################################

def register_macros():
    pass


###############################################################################
# entry points
###############################################################################

def register():
    factory.register_global_preprocessors([plone_preprocessor])
    factory.register_theme('bootstrap', 'yafowil.plone', resourcedir, css=css)


def configure():
    configure_factory()
    register_macros()
