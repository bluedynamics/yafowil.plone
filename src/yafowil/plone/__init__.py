import logging
import pkg_resources


logger = logging.getLogger('yafowil.plone')


IS_PLONE_5 = False
if pkg_resources.require('Products.CMFPlone')[0].version.startswith('5.'):
    IS_PLONE_5 = True


def register():
    if IS_PLONE_5:
        logger.info('Plone 5 detected. Load related YAFOWIL configuration')
        from . import plone5
        plone5.register()
    else:
        logger.info('Plone 4 detected. Load related YAFOWIL configuration')
        from . import plone4
        plone4.register()
