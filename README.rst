This is the **Plone Integration** for `YAFOWIL
<http://pypi.python.org/pypi/yafowil>`_


Functionality
=============


Resources Integration with GenericSetup
---------------------------------------

Addon widgets may provide custom javascripts, CSS, images and so on.

This package registers the directories containing these assets as
resource directories. Thus they can be accessed from the webbrowser.
The registration schema is ``++resource++MODULENAME/...``. 

The "YAFOWIL Form Library" GS profile registers all resources related to
so called "resource groups" in the CSS and javascript registries.

This resource groups must be enabled explicitly(!). The resource groups
configuration happens via the portal registry. 

You need to provide a Generic setup profile containing a ``registry.xml`` with
the resource groups configuration, e.g.::

    <!-- yafowil.widget.array -->
    <record name="yafowil.widget.array.common">
      <field type="plone.registry.field.Bool">
        <title>Array widget common resources</title>
      </field>
      <value>True</value>
    </record>

The record ``name`` maps to the resource group name.

.. note::

    The profile to register the resoures in resource registries (the default
    profile) must run AFTER the resource groups have been configured. Thus you
    are forced to use 2 profiles; one registering the resource groups, and one
    depending on the resource groups profile and the yafowil profile in it's
    ``metadata.xml``. In other words, if you add a plugin
    (like yafowil.widget.autocomplete) ``after yafowil.plone installation``
    you MUST re-install yafowil.plone in order to get new plugin's resources
    registered.

Take a look into ``registry.xml`` of the
``yafowil.plone:profiles/demoresources`` profile for more examples or consider
the referring resource providing code inside the addon widgets, usually
contained in the packages ``__init__.py`` file to get available resource
groups.


Integration with Translation
----------------------------

The package adds an translation method for Zope2 i18n messages. It's added
using by defining a global preprocessor


Request wrapper
---------------

This package registers a global preprocessor for YAFOWIL. It wraps the Zope2
request by an own request instance providing the behavior expected by YAFOWIL.
Spezial behaviors:

File Uploads provided by Zope2 as ``ZPublisher.HTTPRequest.Fileupload``
objects are turned into Dicts with the keys:

**file**
    file-like object to read data from

**filename**
    submitted name of the upload

**mimetype**
    type of the upload

**headers**
    all headers

**original**
    keeps the original ``ZPublisher.HTTPRequest.Fileupload`` object


Base Forms
----------

This package ships with base forms to be extended.

The following form base classes are available:

**yafowil.plone.form.BaseForm**
    does not define a ```__call__``` method: define a template in ZCML or a
    ```__call__``` method. It provides a method named ```render_form```
    which processes and renders the form.

**yafowil.plone.form.Form**
    renders the naked form on ``__call__``.

**yafowil.plone.form.YAMLBaseForm**
    similar to ``BaseForm`` above. Expects properties ``form_template``
    pointing to a YAML file and ``message_factory`` providing the message
    factory used for YAML message strings.

**yafowil.plone.form.YAMLForm**
    similar to ``YAMLBaseForm`` renders the naked YAML form on ``__call__``.

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
    ...         # form widgets creation here...
    ... 
    ...         self.form = form

Convenience for creating YAML forms::

    >>> from zope.i18nmessageid import MessageFactory
    >>> from yafowil.plone.form import YAMLBaseForm

    >>> class MyYAMLForm(YAMLBaseForm):
    ...     action_resource = '@@view_name_callable_by_browser'
    ...     form_template = 'package.name:forms/myform.yaml'
    ...     message_factory = MessageFactory('package.name')

Form classes inherit from ``Products.Five.BrowserPage``, thus they
must be registered via ZCML ``browser:page`` directive::

    <browser:page
      for="*"
      name="form_registration_name"
      class=".forms.MyYAMLForm"
      template="myyamlform.pt"
      permission="cmf.ModifyPortalContent"
    />

Forms build with this base form classes need a template in
order to insert such a form in a layout. It must be called inside a
wrapper template ```myform.yaml```::

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
            <tal:form replace="structure view/render_form" />
          </metal:block>
        </metal:content-core>
      </body>
    </html>


Detailed Documentation
======================

If you're interested to dig deeper: The
`detailed YAFOWIL documentation <http://yafowil.info>`_ is available.
Read it and learn how to create your example application with YAFOWIL.


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
