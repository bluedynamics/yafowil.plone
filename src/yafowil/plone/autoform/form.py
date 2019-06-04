# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition.interfaces import IAcquirer
from plone import api
from plone.app.lockingbehavior.behaviors import ILocking
from plone.dexterity.browser.add import DefaultAddView as DefaultAddViewBase
from plone.dexterity.events import AddBegunEvent
from plone.dexterity.events import AddCancelledEvent
from plone.dexterity.events import EditBegunEvent
from plone.dexterity.events import EditCancelledEvent
from plone.dexterity.events import EditFinishedEvent
from plone.dexterity.i18n import MessageFactory as _dx
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import addContentToContainer
from plone.dexterity.utils import iterSchemata
from plone.dexterity.utils import iterSchemataForType
from plone.locking.interfaces import ILockable
from plone.protect.interfaces import IDisableCSRFProtection
from plone.protect.utils import addTokenToUrl
from plone.registry.interfaces import IRegistry
from plumber import plumbing
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from yafowil.base import factory
from yafowil.plone import _
from yafowil.plone.autoform import directives
from yafowil.plone.autoform import FORM_SCOPE_ADD
from yafowil.plone.autoform import FORM_SCOPE_DISPLAY
from yafowil.plone.autoform import FORM_SCOPE_EDIT
from yafowil.plone.autoform import FORM_SCOPE_HOSTILE_ATTR
from yafowil.plone.autoform.events import ImmediateAddedEvent
from yafowil.plone.autoform.factories import widget_factory
from yafowil.plone.autoform.persistence import YafowilAutoformPersistWriter
from yafowil.plone.autoform.schema import resolve_schemata
from yafowil.plone.form import BaseForm
from yafowil.plone.form import ContentForm
from yafowil.plone.form import CSRFProtectionBehavior
from zExceptions import Redirect
from zope.component import createObject
from zope.component import getUtility
from zope.container.interfaces import INameChooser
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectCreatedEvent

import copy


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

AUTOFORM_BEHAVIOR = {
    'yafowil.autoform',
    'yafowil.plone.autoform.behavior.IYafowilFormBehavior'
}
AUTOFORM_IMMEDIATE_BEHAVIOR = {
    'yafowil.autoform.immediatecreate',
    'yafowil.plone.autoform.behavior.IYafowilImmediateCreateBehavior'
}


class DefaultAddView(DefaultAddViewBase):
    """Replacement of default add view considering whether content type
    uses yafowil forms.
    """

    def __init__(self, context, request, ti):
        behaviors = set(ti.getProperty('behaviors'))
        self.is_yafowil_form = bool(
            (AUTOFORM_BEHAVIOR | AUTOFORM_IMMEDIATE_BEHAVIOR) & behaviors
        )
        if not self.is_yafowil_form:
            return super(DefaultAddView, self).__init__(context, request, ti)
        self.is_immediate = bool(AUTOFORM_IMMEDIATE_BEHAVIOR & behaviors)
        self.context = context
        self.request = request
        self.ti = ti

    def __call__(self):
        if not self.is_yafowil_form:
            return super(DefaultAddView, self).__call__()

        if self.is_immediate:
            if not self.ti.isConstructionAllowed(self.context):
                raise Unauthorized()
            newcontent = api.content.create(
                container=self.context,
                type=self.ti.getId(),
                id="new-{0:s}".format(self.ti.getId()),
                safe_id=True,
                yafowil_immediatecreate="initial",
            )
            notify(ImmediateAddedEvent(newcontent))
            newcontent.indexObject()
            alsoProvides(self.request, IDisableCSRFProtection)
            url = newcontent.absolute_url() + "/immediateadd"
            url = addTokenToUrl(url)
            self.request.response.redirect(url)
            return

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
        # add dummy id to add context, otherwise adding of folderish items
        # will fail
        add_context.id = self.ti.getId()
        checkContentConstraints(self.context, add_context)
        form = AddAutoForm(add_context, self.request, self.ti)
        return form()


###############################################################################
# yafowil base autoform
###############################################################################

def wrap_callables(context, dct):
    # recursively wrap callables into ContextAwareCallable
    for k, v in dct.items():
        if callable(v):
            dct[k] = directives.ContextAwareCallable(context, v)
        if isinstance(v, dict):
            wrap_callables(context, v)
        if isinstance(v, list) or isinstance(v, tuple):
            for it in v:
                wrap_callables(context, it)


@plumbing(CSRFProtectionBehavior)
class BaseAutoForm(BaseForm):
    """Yafowil base autoform.
    """
    ti = None
    form_name = ''

    @property
    def action_triggered(self):
        """Flag whether form action has been triggered.
        """
        actions = [
            self.form['save'],
            self.form['cancel']
        ]
        for action in actions:
            if self.request.get('action.{0}'.format(action.dottedpath)):
                return True
        return False

    def get_schemata(self):
        """Return all schemata to generate form fields for.
        """
        raise NotImplementedError(
            '``BaseAutoForm`` does not implement ``get_schemata``'
        )

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
                'persist_writer': noop_persist_writer
            })
        # resolve schema and add fieldsets to form
        fieldset_definitions = resolve_schemata(self.get_schemata())
        # form order definitions
        order_defs = list()
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
                # XXX: consider schema/behavior name in field name?
                field_name = field_definition.name
                factory_cb = directives.tgv_cache.get_factory_callable(
                    field_definition.schema,
                    field_name
                )
                factory_kw = directives.tgv_cache.get_factory(
                    field_definition.schema,
                    field_name
                )
                # check if factory_callable directive called for field
                if factory_cb:
                    form_field = fieldset[field_name] = factory_cb(self.context)
                # check if factory directive called for field
                elif factory_kw:
                    factory_kw = copy.deepcopy(factory_kw)
                    blueprints = factory_kw.pop('blueprints')
                    wrap_callables(self.context, factory_kw)
                    form_field = fieldset[field_name] = factory(
                        blueprints,
                        **factory_kw
                    )
                # if no directive called for field, use widget_factory
                else:
                    form_field = fieldset[field_name] = widget_factory.widget_for(
                        self.context,
                        field_definition
                    )
                if not form_field.attrs.get('persist_writer'):
                    writer = YafowilAutoformPersistWriter(field_definition)
                    form_field.attrs['persist_writer'] = writer
                # remember order definition for field if defined
                order_def = directives.tgv_cache.get_order(
                    field_definition.schema,
                    field_name
                )
                if order_def:
                    order_defs.append((
                        fieldset_definition.name,
                        field_name,
                        order_def
                    ))
        form['save'] = factory(
            'submit',
            props={
                'action': 'save',
                'expression': True,
                'handler': self.save,
                'next': self.next,
            }
        )
        form['cancel'] = factory(
            'submit',
            props={
                'action': 'cancel',
                'expression': True,
                'skip': True,
                'next': self.cancel,
            }
        )
        # resolve field order
        for fieldset_name, field_name, order_def in order_defs:
            source_fieldset = target_fieldset = form[fieldset_name]
            if order_def['fieldset']:
                target_fieldset = form[order_def['fieldset']]
            if order_def['before']:
                form_field = source_fieldset.detach(field_name)
                anchor_field = target_fieldset[order_def['before']]
                target_fieldset.insertbefore(form_field, anchor_field)
            elif order_def['after']:
                form_field = source_fieldset.detach(field_name)
                anchor_field = target_fieldset[order_def['after']]
                target_fieldset.insertafter(form_field, anchor_field)
            elif order_def['fieldset']:
                form_field = source_fieldset.detach(field_name)
                target_fieldset[field_name] = form_field
        # call form modifiers
        for schema in self.get_schemata():
            for modifier in directives.tgv_cache.get_modifier(schema):
                modifier(self.context, form)

    def save(self, widget, data):
        raise NotImplementedError(
            'Abstract ``BaseAutoForm`` does not implement ``save``'
        )

    def next(self, request):
        raise NotImplementedError(
            'Abstract ``BaseAutoForm`` does not implement ``next``'
        )

    def cancel(self, request):
        raise NotImplementedError(
            'Abstract ``BaseAutoForm`` does not implement ``cancel``'
        )


###############################################################################
# yafowil autoform addform
###############################################################################

class AddAutoForm(BaseAutoForm, ContentForm):
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

    def prepare(self):
        super(AddAutoForm, self).prepare()
        if not self.action_triggered:
            notify(AddBegunEvent(aq_parent(self.context)))

    def save(self, widget, data):
        container = aq_parent(self.context)
        content = createObject(self.ti.factory)
        # Note: The factory may have done this already, but we want to be sure
        # that the created type has the right portal type. It is possible
        # to re-define a type through the web that uses the factory from an
        # existing type, but wants a unique portal_type!
        if hasattr(content, '_setPortalTypeName'):
            content._setPortalTypeName(self.ti.getId())
        # Acquisition wrap temporarily to satisfy things like vocabularies
        # depending on tools
        if IAcquirer.providedBy(content):
            content = content.__of__(container)
        # write data from form to content
        data.write(content)
        # unwrap acquisition
        content = aq_base(content)
        # notify object created
        notify(ObjectCreatedEvent(content))
        # add content to container
        content = addContentToContainer(container, content)
        # remember content id for redirection
        self.new_content_id = content.id
        # set status message
        IStatusMessage(self.request).addStatusMessage(
            _dx(u"Item created"), "info"
        )

    def next(self, request):
        container = aq_parent(self.context)
        next_url = u'{}/{}'.format(
            container.absolute_url(),
            self.new_content_id
        )
        if self.ti.immediate_view:
            next_url = u'{}/{}'.format(next_url, self.ti.immediate_view)
        self.request.response.redirect(next_url)

    def cancel(self, request):
        container = aq_parent(self.context)
        notify(AddCancelledEvent(container))
        IStatusMessage(self.request).addStatusMessage(
            _dx(u"Add New Item operation cancelled"), "info"
        )
        self.request.response.redirect(container.absolute_url())


###############################################################################
# yafowil autoform editform
###############################################################################

class EditAutoForm(BaseAutoForm, ContentForm):
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

    def prepare(self):
        super(EditAutoForm, self).prepare()
        if not self.action_triggered:
            notify(EditBegunEvent(self.context))

    def save(self, widget, data):
        data.write(self.context)
        notify(EditFinishedEvent(self.context))
        IStatusMessage(self.request).addStatusMessage(
            _dx(u"Changes saved"), "info"
        )

    def next(self, request):
        next_url = self.context.absolute_url()
        portal_type = self.context.portal_type
        registry = getUtility(IRegistry)
        use_view_action = registry.get(
            'plone.types_use_view_action_in_listings',
            []
        )
        if portal_type in use_view_action:
            next_url = u'{}/view'.format(next_url)
        self.request.response.redirect(next_url)

    def cancel(self, request):
        notify(EditCancelledEvent(self.context))
        IStatusMessage(self.request).addStatusMessage(
            _dx(u"Edit cancelled"), "info"
        )
        self.request.response.redirect(self.context.absolute_url())


class ImmediateAddAutoForm(EditAutoForm):

    form_name = 'addform'
    action_resource = u'immediateadd'
    success_message = _(u"New content saved")

    @property
    def form_title(self):
        return 'Add {}'.format(self.ti.Title())

    def prepare(self):
        if (
            getattr(self.context, "yafowil_immediatecreate", None) != "initial"
        ):
            url = self.context.absolute_url() + "/edit"
            url = addTokenToUrl(url)
            raise Redirect(url)
        super(ImmediateAddAutoForm, self).prepare()

    def save(self, widget, data):
        data.write(self.context)
        self.context.yafowil_immediatecreate = "created"
        # unlock before rename
        if ILocking.providedBy(self.context):
            lockable = ILockable(self.context)
            if lockable.locked():
                lockable.unlock()
        # rename
        chooser = INameChooser(aq_parent(self.context))
        self.new_content_id = chooser.chooseName(None, self.context)
        api.content.rename(obj=self.context, new_id=self.new_content_id)
        notify(EditFinishedEvent(self.context))
        IStatusMessage(self.request).addStatusMessage(
            _dx(u"Item created"), "info"
        )

    def next(self, request):
        container = aq_parent(self.context)
        next_url = u'{}/{}'.format(
            container.absolute_url(),
            self.new_content_id
        )
        if self.ti.immediate_view:
            next_url = u'{}/{}'.format(next_url, self.ti.immediate_view)
        self.request.response.redirect(next_url)

    def cancel(self, request):
        api.portal.show_message(
            _dx(u"Add New Item operation cancelled"), self.request
        )
        notify(EditCancelledEvent(self.context))
        parent = aq_parent(self.context)
        api.content.delete(obj=self.context)
        self.context = parent
        self.request.response.redirect(self.context.absolute_url())


###############################################################################
# yafowil autoform displayform
###############################################################################

class DisplayAutoForm(BaseAutoForm):
    """Yafowil display form.
    """
    form_name = 'displayform'
    action_resource = u''
    display_fieldsets = ['default']
    skip_fields = []

    def __init__(self, context, request):
        super(DisplayAutoForm, self).__init__(context, request)
        setattr(request, FORM_SCOPE_HOSTILE_ATTR, FORM_SCOPE_DISPLAY)

    def get_schemata(self):
        return iterSchemata(self.context)

    def prepare(self):
        super(DisplayAutoForm, self).prepare()
        origin_form = self.form
        self.form = form = factory('div', name=self.form_name)
        for fieldset in origin_form.values():
            if fieldset.name not in self.display_fieldsets:
                continue
            for widget in fieldset.values():
                if widget.name in self.skip_fields:
                    continue
                form[widget.name] = widget
                widget.mode = 'display'
