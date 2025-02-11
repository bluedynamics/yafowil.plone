
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from io import StringIO
from yafowil.base import factory
from yafowil import bootstrap

import os
import logging
import webresource as wr


logger = logging.getLogger("yafowil.plone")

# exclude yafowil.bootstrap from resources, bootstrap gets delivered via
# barceloneta
excluded_resources = ['yafowil.bootstrap']

resources_dir = os.path.join(os.path.dirname(__file__), 'resources')

resources = wr.ResourceGroup(
    name='yafowil.plone',
    directory=resources_dir,
)

# add popper js from excluded bootstrap resources. datetime widget requires it
resources.add(wr.ScriptResource(
    name='popper-js',
    directory=bootstrap.bs5_scripts_dir,
    resource='popper.min.js'
))

resources.add(wr.ScriptResource(
    name='yafowil-plone-js',
    depends='jquery-js',
    resource='widgets.js'
))

# add bootstrap icons with proper font file path
resources.add(wr.StyleResource(
    name='yafowil-plone-bootstrap-icons-css',
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
        yafowil_resources = factory.get_resources(exclude=excluded_resources)
        return yafowil_resources.scripts


class YafowilCSS(Resources):
    _resource_type = "css"
    _mimetype = "text/css"

    @property
    def yafowil_resources(self):
        yafowil_resources = factory.get_resources(exclude=excluded_resources)
        return yafowil_resources.styles
