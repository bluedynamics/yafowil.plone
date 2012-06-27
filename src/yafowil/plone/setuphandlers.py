import sys
from operator import itemgetter
from yafowil.base import factory
from yafowil.utils import get_plugin_names
from Products.CMFCore.utils import getToolByName


def _extract_resources(which):
    result = list()
    for plugin_name in get_plugin_names():
        resources = factory.resources_for(plugin_name)
        if not resources:
            continue
        for record in resources[which]:
            if record.get('thirdparty', True):
                continue
            if 'order' not in record:
                record['order'] = sys.maxint
            if record['resource'].startswith('http'):
                record['url'] = record['resource']
            else:
                resdirname = '++resource++%s' % plugin_name
                record['url'] = '%s/%s' % (resdirname, record['resource'])
            result.append(record)
    return sorted(result, key=itemgetter('order'))


def setup_resource_registries(context):
    """context: Products.GenericSetup.context.DirectoryImportContext instance
    """
    if not context.readDataFile('yafowil.plone.txt'):
        return
    site = context.getSite()
    msg = 'Stylesheets (CSS)'
    regcss = getToolByName(site, 'portal_css')
    for record in _extract_resources('css'):
        merge = record.get('merge', True)
        msg += '<br />%s' % record['resource']
        if [_ for _ in regcss.getResources() if record['url'] == _.getId()]:
            msg += ' skipped'
            continue
        msg += ' registered'
        regcss.registerStylesheet(record['url'], expression='', media='screen',
            rel='stylesheet', title='', rendering='link', enabled=1,
            cookable=merge, compression='safe', cacheable=True,
            conditionalcomment='', authenticated=False, skipCooking=False,
            applyPrefix=False)
    msg += '<br /><br />Javascripts (JS)'
    regjs = getToolByName(site, 'portal_javascripts')
    for record in _extract_resources('js'):
        merge = record.get('merge', True)
        msg += '<br />%s' % record['resource']
        if [_ for _ in regjs.getResources() if record['url'] == _.getId()]:
            msg += ' skipped'
            continue
        msg += ' registered'
        regjs.registerScript(record['url'], expression='', inline=False,
            enabled=True, cookable=merge, compression='safe', cacheable=True,
            conditionalcomment='', authenticated=False, skipCooking=False)
    return msg
