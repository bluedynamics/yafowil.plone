from node.utils import UNSET
from plone.formwidget.recurrence.browser.i18n import translations
from Products.CMFCore.utils import getToolByName
from yafowil.base import factory
from yafowil.base import fetch_value
from yafowil.common import generic_extractor
from yafowil.common import generic_required_extractor
from yafowil.common import input_attributes_full
from yafowil.utils import attr_value
from yafowil.utils import cssid
from yafowil.utils import managedprops
from zope.component.hooks import getSite


@managedprops('first_day', 'js_field', 'show_repeat_forever')
def recurrence_edit_renderer(widget, data):
    value = fetch_value(widget, data)
    if not value:
        value = ''
    portal = getToolByName(getSite(), 'portal_url').getPortalObject()
    request = data.request.zrequest
    ajax_url = portal.absolute_url() + '/@@json_recurrence'
    first_day = attr_value('first_day', widget, data)
    if first_day is UNSET:
        calendar = request.locale.dates.calendars[u'gregorian']
        first_day = calendar.week.get('firstDay', 0)
    # XXX: start field
    start_field = attr_value('js_field', widget, data)
    if start_field is UNSET:
        start_field = cssid(widget, 'input')
    conf = dict(
        ajaxContentType='application/x-www-form-urlencoded; charset=UTF-8',
        ajaxURL=ajax_url,
        firstDay=first_day,
        hasRepeatForeverButton=attr_value('show_repeat_forever', widget, data),
        lang=request.LANGUAGE,
        readOnly=False,
        ributtonExtraClass='allowMultiSubmit',
        startField=start_field,
    )
    opts = dict(
        localization=translations(request),
        language=request.LANGUAGE,
        configuration=conf
    )
    widget.attrs['data'] = {
        'pat-recurrence': opts
    }
    attrs = input_attributes_full(widget, data)
    attrs['value'] = None
    return data.tag('textarea', value, **attrs)


def recurrence_display_renderer(widget, data):
    value = fetch_value(widget, data)
    return data.tag(
        'span',
        value,
        style='display:none;',
        id=cssid(widget, postfix='start'),
        name='{}-start'.format(widget.dottedpath)
    )


factory.register(
    'recurrence',
    extractors=[
        generic_extractor,
        generic_required_extractor
    ],
    edit_renderers=[recurrence_edit_renderer],
    display_renderers=[recurrence_display_renderer]
)


factory.doc['blueprint']['recurrence'] = """\
Recurrence blueprint.
"""

factory.defaults['recurrence.persist'] = True

factory.defaults['recurrence.type'] = 'textarea'

factory.defaults['recurrence.class'] = 'pat-recurrence recurrence-widget'

factory.defaults['recurrence.show_repeat_forever'] = False

factory.defaults['recurrence.start_field'] = UNSET

factory.defaults['recurrence.js_field'] = UNSET

factory.defaults['recurrence.first_day'] = UNSET
