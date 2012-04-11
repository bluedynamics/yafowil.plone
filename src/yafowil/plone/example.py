import yafowil.plone
import yafowil.loader
from yafowil.base import factory, UNSET
from yafowil.controller import Controller
from zope.i18nmessageid import MessageFactory
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


_ = MessageFactory('Example')


class ExampleView(BrowserView):
    """XXX: outdated -> see ``yafowil.plone.form``
    """

    def _form_action(self, widget, data):
        return '%s/@@yafowil_example_form' % self.context.absolute_url()

    def _form_handler(self, widget, data):
        self.searchterm = data['searchterm'].extracted

    def form(self):
        form = factory('form',
            name='search',
            props={
                'action': self._form_action,
            })
        form['searchterm'] = factory(
            'field:label:error:text',
            props={
                'label': _(u'Search term:'),
                'size': '20',
        })
        form['submit'] = factory(
            'field:submit',
            props={
                'label': _(u'Search'),
                'handler': self._form_handler,
                'action': 'search'
        })
        controller = Controller(form, self.request)
        return controller.rendered

    def results(self):
        if not hasattr(self, 'searchterm') or not self.searchterm:
            return []

        cat = getToolByName(self.context, 'portal_catalog')
        query = {}

        qterm = self.searchterm
        if qterm:
            qterm = '%s' % (qterm)
            query['SearchableText'] = qterm.decode('utf-8')
        return cat(**query)