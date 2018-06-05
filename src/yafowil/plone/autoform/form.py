from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.browser.add import DefaultAddView as DefaultAddViewBase
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import iterSchemata
from plone.dexterity.utils import iterSchemataForType
from plumber import plumbing
from yafowil.base import factory
from yafowil.plone.autoform import FORM_SCOPE_ADD
from yafowil.plone.autoform import FORM_SCOPE_EDIT
from yafowil.plone.autoform import FORM_SCOPE_HOSTILE_ATTR
from yafowil.plone.autoform.factories import widget_factory
from yafowil.plone.autoform.persistence import YafowilAutoformPersistWriter
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
        # XXX: make pat autotoc dedicated blueprint
        pat_autotoc = 'levels: legend; section: fieldset; className: autotabs'
        # XXX: no default persist writer required on widget data
        def noop_persist_writer(model, writer=None, recursiv=True):
            pass
        self.form = form = factory(
            'form',
            name=self.form_name,
            props={
                'action': self.form_action,
                'class': form_class,
                'data': {
                    'pat-autotoc': pat_autotoc
                },
                'persist_writer': noop_persist_writer,
            })
        # resolve schema and add fieldsets to form
        fieldset_definitions = resolve_schemata(self.get_schemata())
        for idx, fieldset_definition in enumerate(fieldset_definitions):
            fieldset_class = 'autotoc-section'
            if idx == 0:
                fieldset_class += ' active'
            fieldset = form[fieldset_definition.name] = factory(
                'fieldset',
                props={
                    'legend': fieldset_definition.label,
                    'class': fieldset_class
                })
            # add fields to fieldset
            for field_definition in fieldset_definition:
                # XXX: consider schema/behavior name in field name
                field_name = field_definition.name
                form_field = fieldset[field_name] = widget_factory.widget_for(
                    self.context,
                    field_definition
                )
                if not form_field.attrs.get('persist_writer'):
                    writer = YafowilAutoformPersistWriter(field_definition)
                    form_field.attrs['persist_writer'] = writer
        self.form['save'] = factory(
            'submit',
            props={
                'action': 'save',
                'expression': True,
                'handler': self.save,
                'next': self.next,
            }
        )
        self.form['cancel'] = factory(
            'submit',
            props={
                'action': 'cancel',
                'expression': True,
                'handler': self.cancel,
                'next': self.next,
            }
        )

    def save(self, widget, data):
        raise NotImplementedError(
            'Abstract ``BaseAutoForm`` does not implement ``save``'
        )

    def cancel(self, widget, data):
        print 'BaseAutoForm.cancel()'

    def next(self, request):
        print 'BaseAutoForm.next()'

    def __call__(self):
        return self.template()


class AddAutoForm(BaseAutoForm):
    """Yafowil add form.
    """
    form_name = 'addform'

    def __init__(self, context, request, ti):
        setattr(request, FORM_SCOPE_HOSTILE_ATTR, FORM_SCOPE_ADD)
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

    def save(self, widget, data):
        print 'AddAutoForm.save()'
        # XXX: trigger object events
        # XXX: name choosing
        # XXX: rename object in container
        child = createContentInContainer(self.context, self.ti.getId())
        data.write(child)


class EditAutoForm(BaseAutoForm):
    """Yafowil edit form.
    """
    form_name = 'editform'
    action_resource = u'edit'

    def __init__(self, context, request):
        setattr(request, FORM_SCOPE_HOSTILE_ATTR, FORM_SCOPE_EDIT)
        super(EditAutoForm, self).__init__(context, request)
        self.ti = getToolByName(
            'portal_types'
        ).getTypeInfo(context.portal_type)

    @property
    def form_title(self):
        return 'Edit {}'.format(self.ti.Title())

    def get_schemata(self):
        return iterSchemata(self.context)

    def save(self, widget, data):
        print 'EditAutoForm.save()'
        # XXX: trigger object events
        data.write(self.context)
