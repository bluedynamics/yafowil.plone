# -*- coding: utf-8 -*-
from collections import MutableMapping
from zope.i18n import translate
from zope.i18nmessageid import Message
from ZPublisher.HTTPRequest import FileUpload
from ZPublisher.HTTPRequest import HTTPRequest

import six


class Zope2RequestAdapter(MutableMapping):
    coding = 'utf-8'

    def __init__(self, request):
        if isinstance(request, self.__class__):
            # for some rare cases this makes sense
            self.zrequest = request.zrequest
        else:
            self.zrequest = request.REQUEST
        if not isinstance(self.zrequest, HTTPRequest):
            raise ValueError('Expecting request based on '
                             'ZPublisher.HTTPRequest.HTTPRequest')

    def __getitem__(self, key):
        value = self.zrequest.form[key]
        if isinstance(value, FileUpload):
            fvalue = dict()
            fvalue['file'] = value
            fvalue['filename'] = value.filename
            fvalue['mimetype'] = value.headers.get('content-type', '')
            fvalue['headers'] = value.headers
            fvalue['original'] = value
            return fvalue
        # XXX: check whether coding is defined on request and ensure proper
        #      decoding
        # XXX: form tag must set accept-charset to ensure proper encoding
        if isinstance(value, six.text_type):
            return value
        return value.decode(self.coding)

    def keys(self):
        return self.zrequest.form.keys()

    def __setitem__(self, key, item):
        raise AttributeError('read only, __setitem__ is not supported')

    def __delitem__(self, key):
        raise AttributeError('read only, __delitem__ is not supported')

    def __len__(self):
        return len(self.zrequest.form)

    def __iter__(self):
        return six.iterkeys(self.zrequest.form.keys())


class ZopeTranslation(object):

    def __init__(self, data):
        self.zrequest = data.request.zrequest

    def __call__(self, msg):
        if not isinstance(msg, Message):
            return msg
        return translate(msg, context=self.zrequest)


def plone_preprocessor(widget, data):
    if not isinstance(data.request, (dict, Zope2RequestAdapter)):
        data.request = Zope2RequestAdapter(data.request)
    if not isinstance(data.translate_callable, ZopeTranslation):
        data.translate_callable = ZopeTranslation(data)
    return data
