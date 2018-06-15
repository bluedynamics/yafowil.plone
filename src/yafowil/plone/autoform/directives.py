# -*- coding: utf-8 -*-
from plone.supermodel.directives import MetadataDictDirective

FACTORY_KEY = 'yafowil.plone.metainfo.factory'
MODIFER_KEY = 'yafowil.plone.metainfo.modifier'
ORDER_KEY = 'yafowil.plone.metainfo.order'


_marker = set()


class factory(MetadataDictDirective):
    """Directive used to define factory infos for
    """
    key = FACTORY_KEY

    def factory(
        self,
        field_name,
        blueprints=_marker,
        value=_marker,
        props=_marker,
        custom=_marker,
        mode=_marker
    ):
        """This is the method expected by MetadataDictDirective returning data
        """
        data = dict()
        if blueprints is not _marker:
            data['blueprints'] = blueprints
        if value is not _marker:
            data['value'] = value
        if props is not _marker:
            data['props'] = props
        if custom is not _marker:
            data['custom'] = custom
        if mode is not _marker:
            data['mode'] = mode
        return {field_name: data}


class order(MetadataDictDirective):
    """Directive used to define factory infos for
    """
    key = ORDER_KEY

    def factory(
        self,
        field_name,
        fieldset=None,
        after=None,
        before=None,
    ):
        data = {
            'fieldset': fieldset,
            'after': after,
            'before': before,
        }
        return {field_name: data}
