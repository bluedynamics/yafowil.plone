# -*- coding: utf-8 -*-
from .behavior import IYafowilImmediateCreateBehavior
from plone.indexer.decorator import indexer


@indexer(IYafowilImmediateCreateBehavior)
def index_in_immediate_creation(obj):
    if obj.yafowil_immediatecreate == "initial":
        return True
    raise AttributeError
