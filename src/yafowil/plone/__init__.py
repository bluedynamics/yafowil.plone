from yafowil.utils import entry_point
from zope.i18nmessageid import MessageFactory
import logging
import os
import pkg_resources


_ = MessageFactory('yafowil.plone')
logger = logging.getLogger('yafowil.plone')


if pkg_resources.require('Products.CMFPlone')[0].version.startswith('5.'):
    logger.debug('Plone 5 detected. Load related YAFOWIL configuration')
    from . import plone5 as yafowil_plone
else:
    logger.debug('Plone 4 detected. Load related YAFOWIL configuration')
    from . import plone4 as yafowil_plone


@entry_point(order=20)
def register():
    yafowil_plone.register()


@entry_point(order=20)
def configure():
    if not os.environ.get('TESTRUN_MARKER'):
        yafowil_plone.configure()
