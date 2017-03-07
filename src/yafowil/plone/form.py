from Products.Five import BrowserView
from plone.keyring.interfaces import IKeyManager
from plone.protect.authenticator import createToken
from plone.protect.utils import getRoot
from plone.protect.utils import getRootKeyManager
from plumber import Behavior
from plumber import plumb
from yafowil.base import factory
from yafowil.controller import Controller
from yafowil.yaml import parse_from_YAML
from zope.component import ComponentLookupError
from zope.component import getUtility


class CSRFProtectionBehavior(Behavior):
    """Plumbing behavior for hooking up CSRF protection to YAFOWIL forms.
    Supposed to be used for AJAX forms.
    """

    @plumb
    def prepare(_next, self):
        """Hook after prepare and set '_authenticator' as proxy field to
        ``self.form``.
        """
        _next(self)
        try:
            key_manager = getUtility(IKeyManager)
        except ComponentLookupError:
            key_manager = getRootKeyManager(getRoot(context))
        self.form['_authenticator'] = factory(
            'proxy',
            value=createToken(manager=key_manager),
        )


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
