from zExceptions import NotFound
from Products.Five import BrowserView
import yafowil.loader
from yafowil.base import factory
from yafowil.utils import get_example, get_example_names


class ExampleResponseView(BrowserView):

    def __call__(self):
        route = self.route(self.request['URL'])
        for header in route.get('header', []):
            self.request.response.setHeader(*header)
        return route.get('body', '')


class ExampleView(BrowserView):

    @property
    def example_names(self):
        return sorted(get_example_names())

    @property
    def example(self):
        if self.example_name:
            return get_example(self.example_name)

    @property
    def example_name(self):
        if hasattr(self, '_example_name'):
            return self._example_name

    @property
    def route(self):
        if hasattr(self, '_route'):
            return self._route

    def _form_action(self, widget, data):
        return '%s/@@yafowil_example_form' % self.context.absolute_url()

    def _form_handler(self, widget, data):
        self.searchterm = data['searchterm'].extracted

    def prepare(self):
        self.form = factory(
            u'form',
            name=self.example_name.replace('.', '-'),
            props={
                'action': 'yafowil_examples/%s' % self.example_name})
        for part in self.example:
            widget = part['widget']
            self.form[widget.name] = widget
        self.form['submit'] = factory(
            'submit',
            props={
                'label': 'submit',
                'action': 'save',
                'handler': lambda widget, data: None})

    def publishTraverse(self, request, name):
        if self.example_name:
            view = ExampleResponseView(self.context, self.request)
            view.routes = dict()
            for part in self.example:
                routes = part.get('routes', [])
                if name in routes:
                    view.route = routes[name]
                    return view
            raise NotFound()
        if name not in self.example_names:
            raise NotFound()
        self._example_name = name
        return self
