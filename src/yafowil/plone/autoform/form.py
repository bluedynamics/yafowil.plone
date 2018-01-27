from yafowil.plone.form import BaseForm
from plone.dexterity.browser.add import DefaultAddView as DefaultAddViewBase


class DefaultAddView(DefaultAddViewBase):

    def __init__(self, context, request, ti):
        print '######## DefaultAddView'
        super(DefaultAddView, self).__init__(context, request, ti)


class BaseAutoForm(BaseForm):
    pass


class AddAutoForm(BaseAutoForm):
    pass


class EditAutoForm(BaseAutoForm):
    pass
