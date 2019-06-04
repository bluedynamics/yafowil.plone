from node.utils import UNSET
from yafowil.base import factory


def datetime_extractor(widget, data):
    pass


def datetime_edit_renderer(widget, data):
    pass


def datetime_display_renderer(widget, data):
    pass


factory.register(
    'plonedatetime',
    extractors=[datetime_extractor],
    edit_renderers=[datetime_edit_renderer],
    display_renderers=[datetime_display_renderer]
)


factory.doc['blueprint']['plonedatetime'] = """\
Datetime blueprint.
"""
