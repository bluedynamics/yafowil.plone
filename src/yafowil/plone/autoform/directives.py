# -*- coding: utf-8 -*-
from plone.supermodel.directives import MetadataDictDirective
from plone.supermodel.directives import MetadataListDirective


FACTORY_KEY = 'yafowil.plone.metainfo.factory'
FACTORY_CALLABLE_KEY = 'yafowil.plone.metainfo.factory_callable'
ORDER_KEY = 'yafowil.plone.metainfo.order'
MODIFIER_KEY = 'yafowil.plone.metainfo.modifier'

_marker = set()


class factory(MetadataDictDirective):
    """Directive used to define yafowil factory call options for a field.
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


class factory_callable(MetadataDictDirective):
    """Directive used to define a callable returning a yafowil widget for a
    schema field.
    """
    key = FACTORY_CALLABLE_KEY

    def factory(self, field_name, func):
        return {field_name: func}


class order(MetadataDictDirective):
    """Directive used to define order infos for a schema field.
    """
    key = ORDER_KEY

    def factory(self, field_name, fieldset=None, after=None, before=None):
        data = {
            'fieldset': fieldset,
            'after': after,
            'before': before,
        }
        return {field_name: data}


class modifier(MetadataListDirective):
    """Directive used to define a form modifier callable.
    """
    key = MODIFIER_KEY

    def factory(self, modifier):
        return [modifier]


class TGVCache(object):
    """Tagged value cache.
    """
    _cache = {
        FACTORY_KEY: {},
        FACTORY_CALLABLE_KEY: {},
        ORDER_KEY: {},
        MODIFIER_KEY: {},
    }

    def _query(self, key, schema):
        tgv = self._cache[key].get(schema, _marker)
        if tgv is _marker:
            tgv = self._cache[key][schema] = schema.queryTaggedValue(key)
        return tgv

    def _query_dict_value(self, key, schema, field_name):
        tgv = self._query(key, schema)
        if tgv:
            val = tgv.get(field_name)
            if val:
                return val
        for base in schema.__bases__:
            val = self._query_dict_value(key, base, field_name)
            if val:
                return val

    def get_factory(self, schema, field_name):
        return self._query_dict_value(FACTORY_KEY, schema, field_name)

    def get_factory_callable(self, schema, field_name):
        return self._query_dict_value(FACTORY_CALLABLE_KEY, schema, field_name)

    def get_order(self, schema, field_name):
        return self._query_dict_value(ORDER_KEY, schema, field_name)

    def get_modifier(self, schema):
        # XXX: modifier gets aggregated from bases. duscuss whether this
        #      behavior is desired
        ret = list()
        modifier = self._query(MODIFIER_KEY, schema)
        if modifier:
            ret += modifier
        for base in schema.__bases__:
            ret += self.get_modifier(base)
        return ret


tgv_cache = TGVCache()


class ContextAwareCallable(object):
    """Any kind of callable can be passed to yafowil factory which gets passed
    the widget instance and the runtime data instance. In case such callables
    are set via ``yafowil.plone.autoform.directives.factory``, additionally
    the context is needed.

    This object acts as bridge between yafowil callable contract, and passes
    ``context``, ``widget`` and ``data`` to callables set via factory directive.
    """

    def __init__(self, context, callback):
        self.context = context
        self.callback = callback
        self.__name__ = callback.__name__
        self.__doc__ = callback.__doc__

    def __call__(self, widget, data):
        return self.callback(self.context, widget, data)
