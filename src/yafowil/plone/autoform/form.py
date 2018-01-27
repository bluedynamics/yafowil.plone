from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.browser.add import DefaultAddView as DefaultAddViewBase
from plone.dexterity.utils import iterSchemata
from plone.dexterity.utils import iterSchemataForType
from plumber import plumbing
from yafowil.base import factory
from yafowil.plone.autoform.factories import widget_factory
from yafowil.plone.autoform.schema import resolve_schemata
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
    form_title = ''
    template = ViewPageTemplateFile('../content.pt')

    def get_schemata(self):
        """Return all schemata to generate form fields for.
        """
        raise NotImplementedError(
            '``BaseAutoForm`` does not implement ``get_schemata``')

    def prepare(self):
        form_class = (
            'rowlike pat-formunloadalert enableFormTabbing pat-autotoc '
            'view-name-add-Folder autotabs'
        )
        pat_autotoc = 'levels: legend; section: fieldset; className: autotabs'
        self.form = form = factory(
            'form',
            name=self.form_name,
            props={
                'action': self.form_action,
                'class': form_class,
                'data': {
                    'pat-autotoc': pat_autotoc
                }
            })
        # lookup schema definitions
        schema_definitions = resolve_schemata(self.get_schemata())
        # add fieldsets to form
        fieldset_definitions = schema_definitions['fieldsets'].values()
        for idx, fieldset_definition in enumerate(fieldset_definitions):
            fieldset_class = 'autotoc-section'
            if idx == 0:
                fieldset_class += ' active'
            fieldset = form[fieldset_definition.__name__] = factory(
                'fieldset',
                props={
                    'legend': fieldset_definition.label,
                    'class': fieldset_class
                })
            # add fields to fieldset
            for field_name in fieldset_definition.fields:
                fieldset[field_name] = widget_factory.widget_for(
                    self.context,
                    schema_definitions['fields'][field_name]
                )

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
        request._yafowil_autoform_scope = 'add'
        super(AddAutoForm, self).__init__(context, request)
        self.ti = ti


    @property
    def form_title(self):
        return 'Add {}'.format(self.ti.Title())

    @property
    def action_resource(self):
        return u'++add++{tid}'.format(tid=self.ti.getId())

    def get_schemata(self):
        return iterSchemataForType(self.ti.getId())


class EditAutoForm(BaseAutoForm):
    """Yafowil edit form.
    """
    form_name = 'editform'
    action_resource = u'edit'

    def __init__(self, context, request):
        request._yafowil_autoform_scope = 'edit'
        super(EditAutoForm, self).__init__(context, request)
        self.ti = getToolByName('portal_types').getTypeInfo(context.portal_type)

    @property
    def form_title(self):
        return 'Edit {}'.format(self.ti.Title())

    def get_schemata(self):
        return iterSchemata(self.context)
