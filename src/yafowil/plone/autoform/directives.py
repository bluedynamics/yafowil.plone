# -*- coding: utf-8 -*-
from plone.supermodel.directives import MetadataDictDirective
from plone.supermodel.directives import MetadataListDirective

FACTORY_KEY = 'yafowil.plone.metainfo.factory'
ORDER_KEY = 'yafowil.plone.metainfo.order'
MODIFER_KEY = 'yafowil.plone.metainfo.modifier'


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
        """This is the method expected by MetadataDictDirective returning data.
        Dont be confused aout the name 'factory' here.
        It is the api name expected by the super class in plone.supermodel.
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
    """Directive used to define order infos for a schema field
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


class modifier(MetadataListDirective):
    """Directive used to define factory infos for
    """
    key = MODIFER_KEY

    def factory(
        self,
        modifier,
    ):
        return [modifier]
