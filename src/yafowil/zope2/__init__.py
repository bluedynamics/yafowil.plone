from UserDict import DictMixin
from zope.i18n import translate
from zope.i18nmessageid import Message
from ZPublisher.HTTPRequest import HTTPRequest, FileUpload
from yafowil.base import factory

class Zope2RequestAdapter(DictMixin):
    
    def __init__(self, context):
        if isinstance(context, HTTPRequest):
            raise ValueError, 'In Zope 2 pass in the context, not the request!'
        if isinstance(context, self.__class__):
            # for some rare cases this makes sense             
            self.zrequest = context.zrequest
            self.context = context.context 
        else:
            self.zrequest = context.REQUEST
            self.context = context 
        if not isinstance(self.zrequest, HTTPRequest):
            raise ValueError(\
                'Expecting request based on ZPublisher.HTTPRequest.HTTPRequest') 
        
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
        return value

    def keys(self):
        return self.zrequest.form.keys()
    
    def __setitem__(self, key, item):
        raise AttributeError('read only, __setitem__ is not supported')
    
    def __delitem__(self, key):
        raise AttributeError('read only, __delitem__ is not supported')
    
class ZopeTranslation(object):
    
    def __init__(self, data):
        self.context = data.request.context
        
    def __call__(self, msg):
        if not isinstance(msg, Message):
            return msg            
        return translate(msg, context=self.context)
    
def zope2_preprocessor(widget, data):
    if not isinstance(data.request, (dict, Zope2RequestAdapter)):
        data.request = Zope2RequestAdapter(data.request)
    if not isinstance(data.translate_callable, ZopeTranslation):
        data.translate_callable = ZopeTranslation(data)    
    return data

factory.register_global_preprocessors([zope2_preprocessor])