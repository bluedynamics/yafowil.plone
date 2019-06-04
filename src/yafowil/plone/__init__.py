from yafowil.plone import config
from yafowil.utils import entry_point
from zope.i18nmessageid import MessageFactory

import logging
import os


_ = MessageFactory('yafowil.plone')
logger = logging.getLogger('yafowil.plone')


@entry_point(order=20)
def register():
    config.register()


@entry_point(order=20)
def configure():
    if not os.environ.get('TESTRUN_MARKER'):
        config.configure()
