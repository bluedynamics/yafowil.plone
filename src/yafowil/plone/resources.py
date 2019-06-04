from operator import itemgetter
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from six import StringIO
from yafowil.base import factory
from yafowil.utils import get_plugin_names
from zope.component import getUtility

import logging
import os
import sys


logger = logging.getLogger('yafowil.plone')


def enabled_resources(which, verbose=True):
    """Return enabled YAFOWIL resources.

    ``which`` is either "js" or "css".
    """
    result = list()
    registry = getUtility(IRegistry)
    for plugin_name in get_plugin_names():
        resources = factory.resources_for(plugin_name)
        if not resources:
            continue
        resourcedir = resources['resourcedir']
        for record in resources[which]:
            if not registry.get(record['group']):
                verbose and logger.warning(
                    "Skipping resource '%s' for group '%s'" % (
                        record['resource'], record['group']
                    )
                )
                continue
            if 'order' not in record:
                record['order'] = sys.maxint
            if record['resource'].startswith('http'):
                record['url'] = record['resource']
                record['path'] = None
            else:
                resdirname = '++resource++%s' % plugin_name
                record['url'] = '%s/%s' % (resdirname, record['resource'])
                record['path'] = os.path.join(resourcedir, record['resource'])
            result.append(record)
            verbose and logger.info(
                "Activate resource '%s' for group '%s' order: '%s'" % (
                    record['resource'], record['group'], record['order']
                )
            )
    return sorted(result, key=itemgetter('order'))


class Resources(BrowserView):
    """Browser view for concatenating and delivering resources defined in
    YAFOWIL resource groups.

    This code is inspired by resource delivery views in collective.js.jqueryui.

    Plone 5 only.
    """
    _header_template = u"\n/* yafowil.plone: %s */\n"
    _resource_type = None
    _mimetype = None

    def __call__(self):
        self.request.response.setHeader('Content-Type', self._mimetype)
        return self.get_resources_content(
            enabled_resources(self._resource_type)
        )

    def get_resources_content(self, resources):
        data = StringIO()
        data.write(self._header_template % (self._resource_type))
        data.write(u"\n")
        for resource in resources:
            if resource['path'] is None:
                logger.error('Remote YAFOWIL resource found which cannot be '
                             'included in bundle {}'.format(resource['url']))
                continue
            with open(resource['path'], 'r') as fd:
                content = fd.read()
            content = safe_unicode(content)
            data.write(content)
            data.write(u"\n")
        return data.getvalue()


class YafowilJS(Resources):
    _resource_type = 'js'
    _mimetype = 'application/javascript'


class YafowilCSS(Resources):
    _resource_type = 'css'
    _mimetype = 'text/css'
