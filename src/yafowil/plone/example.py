import yafowil.plone
import yafowil.loader
from yafowil.base import factory
from yafowil.utils import get_example
from .form import BaseForm


class ExampleForm(BaseForm):

    def _form_action(self, widget, data):
        return '%s/@@yafowil_example_form' % self.context.absolute_url()

    def _form_handler(self, widget, data):
        self.searchterm = data['searchterm'].extracted

    def prepare(self):
        plugin_name = 'yafowil'
        example = get_example(plugin_name)
        self.form = factory(
            u'form',
            name=plugin_name.replace('.', '-'),
            props={
                'action': 'yafowil_example_form/%s' % plugin_name})
        for part in example:
            widget = part['widget']
            self.form[widget.name] = widget
        self.form['submit'] = factory(
            'submit',
            props={
                'label': 'submit',
                'action': 'save',
                'handler': lambda widget, data: None})
