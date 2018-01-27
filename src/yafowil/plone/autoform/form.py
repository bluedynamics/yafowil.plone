from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.browser.add import DefaultAddView as DefaultAddViewBase
from plumber import plumbing
from yafowil.base import factory
from yafowil.plone.form import BaseForm
from yafowil.plone.form import CSRFProtectionBehavior


class DefaultAddView(DefaultAddViewBase):
    """Replacement of default add view considering whether content type
    uses yafowil forms.
    """

    def __init__(self, context, request, ti):
        behaviors = ti.getProperty('behaviors')
        self.is_yafowil_form = (
            'yafowil.autoform' in behaviors or
            'yafowil.plone.autoform.behavior.IYafowilFormBehavior' in behaviors
        )
        if not self.is_yafowil_form:
            return super(DefaultAddView, self).__init__(context, request, ti)
        self.context = context
        self.request = request
        self.ti = ti

    def __call__(self):
        if not self.is_yafowil_form:
            return super(DefaultAddView, self).__call__()
        form = AddAutoForm(self.context, self.request, self.ti)
        return form()


@plumbing(CSRFProtectionBehavior)
class BaseAutoForm(BaseForm):
    """Yafowil base autoform.
    """
    form_name = ''
    template = ViewPageTemplateFile('../content.pt')

    def prepare(self):
        self.form = form = factory(
            'form',
            name=self.form_name,
            props={
                'action': self.form_action,
            })
        form['test'] = factory(
            '#field:text',
            value='Hallo Yafowil World',
            props={
                'label': 'YAY',
                'help': 'I am from yafowil'
            })

    def save(self, widget, data):
        print 'BaseAutoForm.save()'
        #data.write(self.context)

    def __call__(self):
        return self.template()


class AddAutoForm(BaseAutoForm):
    """Yafowil add form.
    """
    form_name = 'addform'

    def __init__(self, context, request, ti):
        super(AddAutoForm, self).__init__(context, request)
        self.ti = ti

    @property
    def action_resource(self):
        return u'++add++{tid}'.format(tid=self.ti.getId())


class EditAutoForm(BaseAutoForm):
    """Yafowil edit form.
    """
    form_name = 'editform'
    action_resource = u'edit'

    def __init__(self, context, request):
        super(EditAutoForm, self).__init__(context, request)
        self.ti = getToolByName('portal_types').getTypeInfo(context.portal_type)
