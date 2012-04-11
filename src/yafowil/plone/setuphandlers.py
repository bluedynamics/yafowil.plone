from yafowil.utils import (
    get_javascripts,
    get_stylesheets,
    get_plugin_names,
)
from Products.CMFCore.utils import getToolByName


def setup_resource_registries(context):
    """context: Products.GenericSetup.context.DirectoryImportContext instance
    """
    if not context.readDataFile('yafowil.plone.txt'):
        return
    msg = ''
    js = []
    for module_name in get_plugin_names('javascripts'):
        prefix = '++resource++%s/' % module_name    
        js += [(prefix + _) for _ in get_javascripts(module_name, 
                                                     thirdparty=False)]
    css = []
    for module_name in get_plugin_names('stylesheets'):
        prefix = '++resource++%s/' % module_name
        css += [(prefix + _) for _ in get_stylesheets(module_name, 
                                                      thirdparty=False)]
    site = context.getSite()
    regcss = getToolByName(site, 'portal_css')
    msg += 'Stylesheets (CSS)'
    for resource_id in sorted(css):
        msg += '<br />%s' % resource_id
        if [_ for _ in regcss.getResources() if resource_id == _.getId()]:
            msg += ' skipped'
            continue      
        msg += ' registered'
        regcss.registerStylesheet(resource_id, expression='', media='screen',
            rel='stylesheet', title='', rendering='link', enabled=1,
            cookable=True, compression='safe', cacheable=True,
            conditionalcomment='', authenticated=False, skipCooking=False,
            applyPrefix=False)
    regjs  = getToolByName(site, 'portal_javascripts')
    msg += '<br /><br />Javascripts (JS)'
    for resource_id in sorted(js):
        msg += '<br />%s' % resource_id
        if [_ for _ in regjs.getResources() if resource_id == _.getId()]:
            msg += ' skipped'
            continue      
        msg += ' registered'
        regjs.registerScript(resource_id, expression='', inline=False,
            enabled=True, cookable=True, compression='safe', cacheable=True,
            conditionalcomment='', authenticated=False, skipCooking=False)
    return msg