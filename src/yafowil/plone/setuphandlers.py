from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Do not show on Plone's list of installable profiles."""
        return [
            #"yafowil.plone:demo",
        ]
