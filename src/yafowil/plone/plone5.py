from yafowil.base import factory
from yafowil.plone.connectors import plone_preprocessor
import os


resourcedir = os.path.join(os.path.dirname(__file__), 'plone5')
css = [{
    'group': 'bootstrap.glyphicons',
    'resource': 'glyphicons.css',
    'order': 10,
}]


PLONE_MACROS = {
}


def register():
    factory.register_global_preprocessors([plone_preprocessor])
    factory.register_theme('bootstrap', 'yafowil.plone', resourcedir, css=css)
    for name, value in PLONE_MACROS.items():
        factory.register_macro(name, value['chain'], value['props'])
