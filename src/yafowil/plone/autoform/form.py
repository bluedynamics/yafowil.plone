from AccessControl import Unauthorized
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone.dexterity.browser.add import DefaultAddView as DefaultAddViewBase
from plone.dexterity.events import AddCancelledEvent
from plone.dexterity.i18n import MessageFactory as _dx
from plone.dexterity.interfaces import IDexterityFTI
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
from zope.component import createObject
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent


###############################################################################
# plone.dexterity.utils related
###############################################################################

def createContent(portal_type, suppressNotify=False, **kw):
    """Same function as ``plone.dexterity.utils.createContent`` except
    ``suppressNotify`` keyword argument in signature.

    XXX: Update original function in ``plone.dexterity.utils``.
    """
    fti = getUtility(IDexterityFTI, name=portal_type)
    content = createObject(fti.factory)

    # Note: The factory may have done this already, but we want to be sure
    # that the created type has the right portal type. It is possible
    # to re-define a type through the web that uses the factory from an
    # existing type, but wants a unique portal_type!
    content.portal_type = fti.getId()
    schemas = iterSchemataForType(portal_type)
    fields = dict(kw)  # create a copy

    for schema in schemas:
        # schema.names() doesn't return attributes from superclasses in derived
        # schemas. therefore we have to iterate over all items from the passed
        # keywords arguments and set it, if the behavior has the questioned
        # attribute.
        behavior = schema(content)
        for name, value in fields.items():
            try:
                # hasattr swallows exceptions.
                getattr(behavior, name)
            except AttributeError:
                # fieldname not available
                continue
            setattr(behavior, name, value)
            del fields[name]

    for (key, value) in fields.items():
        setattr(content, key, value)

    if not suppressNotify:
        notify(ObjectCreatedEvent(content))
    return content


def checkContentConstraints(container, child):
    """Check whether child is allowed in container.

    XXX: Move to ``plone.dexterity.utils`` and use in ``addContentToContainer``.
    """
    container = aq_inner(container)
    container_fti = container.getTypeInfo()
    fti = getUtility(IDexterityFTI, name=child.portal_type)
    if not fti.isConstructionAllowed(container):
        raise Unauthorized('Cannot create {}'.format(child.portal_type))
    if container_fti is not None \
        and not container_fti.allowType(child.portal_type):
        msg = 'Disallowed subobject type: {}'.format(child.portal_type)
        raise ValueError(msg)


###############################################################################
# default add view
###############################################################################

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
        # Create dummy add context. Used to render the add form.
        # This context does not get persisted. It's just used to render the
        # add form and gets dropped afterwards. In order to make this work
        # we need to do acquisition wrapping.
        # Yafowil autoforms behave differently from autoforms based on z3zform
        # here. We're convinced that having the correct context a form is
        # supposed to be rendered on is the way a form engine must work.
        add_context = createContent(
            self.ti.getId(),
            suppressNotify=True
        ).__of__(aq_inner(self.context))
        checkContentConstraints(self.context, add_context)
        form = AddAutoForm(add_context, self.request, self.ti)
        return form()


###############################################################################
# yafowil base autoform
###############################################################################

@plumbing(CSRFProtectionBehavior)
class BaseAutoForm(BaseForm):
    """Yafowil base autoform.
    """
    ti = None
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
                'skip': True,
                'next': self.cancel,
            }
        )

    def save(self, widget, data):
        raise NotImplementedError(
            'Abstract ``BaseAutoForm`` does not implement ``save``'
        )

    def cancel(self, request):
        self.request.response.redirect(self.context.absolute_url())

    def next(self, request):
        self.request.response.redirect(self.context.absolute_url())

    def __call__(self):
        return self.template()


###############################################################################
# yafowil autoform addform
###############################################################################

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

    def form_action(self, widget, data):
        action_resource = u'++add++{tid}'.format(tid=self.ti.getId())
        return u'%s/%s' % (aq_parent(self.context).absolute_url(), action_resource)

    def get_schemata(self):
        return iterSchemataForType(self.ti.getId())

    def save(self, widget, data):
        container = aq_parent(self.context)
        child = createContentInContainer(container, self.ti.getId())
        data.write(child)

    def cancel(self, request):
        container = aq_parent(self.context)
        notify(AddCancelledEvent(container))
        IStatusMessage(self.request).addStatusMessage(
            _dx(u"Add New Item operation cancelled"), "info"
        )
        self.request.response.redirect(container.absolute_url())

    def next(self, request):
        immediate_view = self.ti.immediate_view
        next_url = self.context.absolute_url()
        if immediate_view:
            next_url = u'{}/{}'.format(next_url, immediate_view)
        self.request.response.redirect(next_url)


###############################################################################
# yafowil autoform editform
###############################################################################

class EditAutoForm(BaseAutoForm):
    """Yafowil edit form.
    """
    form_name = 'editform'
    action_resource = u'edit'

    def __init__(self, context, request):
        setattr(request, FORM_SCOPE_HOSTILE_ATTR, FORM_SCOPE_EDIT)
        super(EditAutoForm, self).__init__(context, request)
        self.ti = getToolByName(
            self.context,
            'portal_types'
        ).getTypeInfo(context.portal_type)

    @property
    def form_title(self):
        return 'Edit {}'.format(self.ti.Title())

    def get_schemata(self):
        return iterSchemata(self.context)

    def save(self, widget, data):
        # XXX: trigger object events
        data.write(self.context)
