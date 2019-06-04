from __future__ import absolute_import
from datetime import date
from datetime import datetime
from node.utils import UNSET
from plone.app.widgets.utils import get_date_options
from plone.app.widgets.utils import get_datetime_options
from Products.CMFPlone.utils import safe_callable
from yafowil.base import factory
from yafowil.base import fetch_value
from yafowil.common import generic_extractor
from yafowil.common import generic_required_extractor
from yafowil.common import input_generic_renderer
from yafowil.utils import attr_value
from yafowil.utils import managedprops
from zope.component.hooks import getSite

import pytz


@managedprops('include_time', 'default_timezone')
def datetime_extractor(widget, data):
    extracted = data.extracted
    if extracted is UNSET:
        return extracted
    if not extracted:
        # XXX: default/missing value
        return None
    if attr_value('include_time', widget, data):
        tmp = extracted.split(' ')
        if not tmp[0]:
            # XXX: default/missing value
            return None
        value = tmp[0].split('-')
        if len(tmp) == 2 and ':' in tmp[1]:
            value += tmp[1].split(':')
        else:
            value += ['00', '00']
        # TODO: respect the selected zone from the widget and just fall back
        # to default_zone
        default_zone = attr_value('default_timezone', widget, data)
        zone = default_zone(getSite()) if safe_callable(default_zone) else default_zone
        ret = datetime(*map(int, value))
        if zone and not isinstance(zone, pytz.tzinfo.BaseTzInfo):
            zone = pytz.timezone(zone)
        if zone:
            ret = zone.localize(ret)
        return ret
    else:
        return date(*map(int, value.split('-')))


@managedprops('include_time')
def datetime_edit_renderer(widget, data):
    request = data.request.zrequest
    if attr_value('include_time', widget, data):
        opts = get_datetime_options(request)
        value = fetch_value(widget, data)
        if value:
            value = (
                '{value.year:}-{value.month:02}-{value.day:02} '
                '{value.hour:02}:{value.minute:02}'
            ).format(value=value)
        else:
            value = ''
    else:
        opts = get_date_options(request)
        value = fetch_value(widget, data)
        if value:
            value = (
                '{value.year:}-{value.month:02}-{value.day:02}'
            ).format(value=value)
        else:
            value = ''
    if attr_value('required', widget, data):
        opts['clear'] = False
    widget.attrs['data'] = {
        'pat-pickadate': opts
    }
    return input_generic_renderer(widget, data, custom_attrs=dict(value=value))


def datetime_display_renderer(widget, data):
    return '<div>Date Display Renderer</div>'


factory.register(
    'plonedatetime',
    extractors=[
        generic_extractor,
        generic_required_extractor,
        datetime_extractor
    ],
    edit_renderers=[datetime_edit_renderer],
    display_renderers=[datetime_display_renderer]
)


factory.doc['blueprint']['plonedatetime'] = """\
Datetime blueprint.
"""

factory.defaults['plonedatetime.persist'] = True

factory.defaults['plonedatetime.class'] = 'pat-pickadate'

factory.defaults['plonedatetime.include_time'] = True

factory.defaults['plonedatetime.default_timezone'] = None
