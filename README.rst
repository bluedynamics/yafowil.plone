This is the **Zope2 integration** for `YAFOWIL
<http://pypi.python.org/pypi/yafowil>`_


Functionality
=============

Browser Resources
-----------------

Plugins may provide custom javascript, css, images (and so on). This package
registers the directory containing them as a resource-directory. Thus they can
be accessed from the webbrowser. The schema is
``+++resource++MODULENAME/filename.ext``. I.e. if
``yafowil.widget.autocomplete`` is available its javascript can be accessed
with
``http://localhost:8080/Plone/++resource++yafowil.widget.autocomplete/widget.js``.


Integration with Plone and GenericSetup
---------------------------------------

There is a profile ``YAFOWIL`` available registering all browser resources in
css and javascript registries.

The resources are registred without any thridparty dependencies (i.e. dependend
javascript libraries).


Integration with Translation
----------------------------

The package adds an translation method for Zope2 i18n messages. Its added using
a global preprocessor


Request wrapper
---------------

This package registers a global preprocessor for YAFOWIL. It wraps the Zope2
request by an own request instance providing the behavior expected by YAFOWIL.
Spezial behaviors:

- File Uploads provided by Zope2 as ``ZPublisher.HTTPRequest.Fileupload``
  objects are turned into Dicts with the keys:

  file
      file-like object to read data from

  filename
      submitted name of the upload

  mimetype
      type of the upload

  headers
      all headers

  original
      keeps the original ``ZPublisher.HTTPRequest.Fileupload`` object


Base Forms
----------

This package ships with base forms to be extended.

Concrete implementation may look like::
    
    >>> from yafowil.base import factory
    >>> from yafowil.plone.form import Form
    
    >>> class MyForm(Form):
    ...     action_resource = '@@view_name_callable_by_browser'
    ...     
    ...     def prepare(self):
    ...         form = factory(
    ...             'form',
    ...             name='myform',
    ...             props={
    ...                 'action': self.form_action,
    ...             })
    ... 
    ...         # form field manufactoring here...
    ... 
    ...         self.form = form

Convenience for creating YAML forms::

    >>> from zope.i18nmessageid import MessageFactory
    >>> from yafowil.plone.form import YAMLForm
    
    >>> class MyYAMLForm(YAMLForm):
    ...     action_resource = '@@view_name_callable_by_browser'
    ...     form_template = 'package.name:forms/myform.yaml'
    ...     message_factory = MessageFactory('package.name')

Both base form classes inherit from ``Products.Five.BrowserPage``, thus they
must be registered via ZCML ``browser:page`` directive::

    <browser:page
      for="*"
      name="form_registration_name"
      class=".forms.MyYAMLForm"
      permission="cmf.ModifyPortalContent"
    />

Forms build with this base form classes are rendered without any wrapper, in
order to insert such a form in a layout it must be called inside a
wrapper template (plone example)::

    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
          xmlns:tal="http://xml.zope.org/namespaces/tal"
          xmlns:metal="http://xml.zope.org/namespaces/metal"
          xmlns:i18n="http://xml.zope.org/namespaces/i18n"
          lang="en"
          metal:use-macro="context/main_template/macros/master"
          i18n:domain="package.name">
      <body>
        <metal:content-core fill-slot="content-core">
          <metal:block define-macro="content-core">
            <tal:form replace="structure context/@@form_registration_name" />
          </metal:block>
        </metal:content-core>
      </body>
    </html>


Source Code
===========

The sources are in a GIT DVCS with its main branches at
`github <http://github.com/bluedynamics/yafowil.plone>`_.


Contributors
============

- Jens W. Klein <jens [at] bluedynamics [dot] com>

- Peter Holzer <hpeter [at] agitator [dot] com>

- Benjamin Stefaner <bs [at] kleinundpartner [dot] at>

- Robert Niederreiter <rnix [at] squarewave [dot] at>
