from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import interfaces as Plone
from Products.CMFQuickInstallerTool import interfaces as QuickInstaller
from yafowil.plone.resources import enabled_resources
from zope.interface import implementer


@implementer(Plone.INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Do not show on Plone's list of installable profiles.
        """
        return [
            'yafowil.plone:demo',
            'yafowil.plone:demoresources'
        ]


@implementer(QuickInstaller.INonInstallable)
class HiddenProducts(object):

    def getNonInstallableProducts(self):
        """Do not show on QuickInstaller's list of installable products.
        """
        return [
            'yafowil.plone:demo',
            'yafowil.plone:demoresources'
        ]


def setup_resource_registries(context):
    """Registers all enabled yafowil resource groups to portal_css and
    portal_javascripts.

    Plone 4 only.

    ``context`` is a Products.GenericSetup.context.DirectoryImportContext
    instance.
    """
    if not context.readDataFile('yafowil.plone.txt'):
        return
    site = context.getSite()
    msg = 'Stylesheets (CSS)'
    regcss = getToolByName(site, 'portal_css')
    for record in enabled_resources('css', verbose=True):
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
            applyPrefix=True)
    msg += '<br /><br />Javascripts (JS)'
    regjs = getToolByName(site, 'portal_javascripts')
    for record in enabled_resources('js', verbose=True):
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
