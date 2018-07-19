from DateTime import DateTime
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class YafowilAutoformPersistWriter(object):

    def __init__(self, field):
        self.field = field

    def __call__(self, model, target, value):
        # XXX: only write if changed
        if self.field.is_behavior:
            setattr(self.field.schema(model), target, value)
        else:
            setattr(model, target, value)


class RichtextPersistWriter(YafowilAutoformPersistWriter):

    def __call__(self, model, target, value):
        # XXX: extract mimetype from request
        mime_type = self.field.schemafield.default_mime_type
        output_mime_type = self.field.schemafield.output_mime_type
        value = RichTextValue(
            raw=value if value else '',
            mimeType=mime_type,
            outputMimeType=output_mime_type
        )
        super(RichtextPersistWriter, self).__call__(model, target, value)


class AjaxSelectPersistWriter(YafowilAutoformPersistWriter):

    def __call__(self, model, target, value):
        if not value:
            value = tuple()
        else:
            seperator = self.field.widget.params.get('separator', ';')
            value = tuple(value.split(seperator))
        super(AjaxSelectPersistWriter, self).__call__(model, target, value)


class RelatedItemsPersistWriter(YafowilAutoformPersistWriter):

    def __call__(self, model, target, value):
        if not value:
            value = list()
        else:
            seperator = self.field.widget.params.get('separator', ';')
            intids = getUtility(IIntIds)
            rels = list()
            for item in value.split(seperator):
                if not item:
                    continue
                # XXX: try/except
                to_id = intids.getId(uuidToObject(item))
                rels.append(RelationValue(to_id))
            value = rels
        super(RelatedItemsPersistWriter, self).__call__(model, target, value)
