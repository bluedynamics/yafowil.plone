
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from io import StringIO
from yafowil.base import factory

import os
import logging
import webresource as wr


logger = logging.getLogger("yafowil.plone")


resources_dir = os.path.join(os.path.dirname(__file__), 'resources')


resources = wr.ResourceGroup(
    name='yafowil.plone',
    directory=resources_dir,
    path='yafowil-plone'
)
resources.add(wr.ScriptResource(
    name='yafowil-plone-js',
    path='yafowil-plone',
    depends='jquery-js',
    resource='widgets.js'
))
resources.add(wr.StyleResource(
    name='yafowil-plone-bootstrap-icons-css',
    path='yafowil-plone',
    resource='bootstrap-icons.css'
))


class Resources(BrowserView):
    """Browser view for concatenating and delivering YAFOWIL resources"""

    _header_template = "\n/* yafowil.plone: %s */\n"
    _resource_type = None
    _mimetype = None

    def __call__(self):
        self.request.response.setHeader("Content-Type", self._mimetype)
        data = StringIO()
        for resource in self.yafowil_resources:
            try:
                data.write(safe_unicode(resource.file_data))
            except Exception as e:
                logger.exception(e)
                continue
            data.write("\n")
        return data.getvalue()


class YafowilJS(Resources):
    _resource_type = "js"
    _mimetype = "application/javascript"

    @property
    def yafowil_resources(self):
        yafowil_resources = factory.get_resources(exclude=['yafowil.bootstrap'])
        return yafowil_resources.scripts


class YafowilCSS(Resources):
    _resource_type = "css"
    _mimetype = "text/css"

    @property
    def yafowil_resources(self):
        yafowil_resources = factory.get_resources(exclude=['yafowil.bootstrap'])
        return yafowil_resources.styles
