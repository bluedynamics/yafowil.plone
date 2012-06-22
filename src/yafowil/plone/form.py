from yafowil.controller import Controller
from yafowil.yaml import parse_from_YAML
from Products.Five import BrowserView


class BaseForm(BrowserView):
    form = None
    action_resource = u''

    def form_action(self, widget, data):
        return '%s/%s' % (self.context.absolute_url(), self.action_resource)

    def render_form(self):
        self.prepare()
        controller = Controller(self.form, self.request)
        if not controller.next:
            return controller.rendered
        return controller.next

    def prepare(self):
        raise NotImplementedError(u"Abstract Form does not implement "
                                  u"``prepare``.")


class Form(BaseForm):

    def __call__(self):
        return self.render_form()


class YAMLBaseForm(BaseForm):
    form_template = None
    message_factory = None

    def prepare(self):
        self.form = parse_from_YAML(
            self.form_template, self, self.message_factory)


class YAMLForm(YAMLBaseForm):

    def __call__(self):
        return self.render_form()
