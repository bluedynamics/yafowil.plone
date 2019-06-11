.. image:: https://travis-ci.com/bluedynamics/yafowil.plone.svg?branch=master
    :target: https://travis-ci.com/bluedynamics/yafowil.plone

`YAFOWIL <http://pypi.python.org/pypi/yafowil>`_ is a form library for Python.
This is its **Plone Integration** package

Overview
========

*yafowil.plone* offers different levels of integration for Plone:

- wraps the Zope Request to fullfill YAFOWIL expectations
- combines and registers CSS and JavScript Resources
- a YAFOWIL theme for the widgets
- macros following Plone default markup for fields, labels, ...
- Plone specific widgets
- l10n/i18n integration
- base forms for use in views (Python and YAML based)
- autoform features (still experimental):
  - generates forms from zope.schema and schema annotations
  - works as drop-in replacement for z3c.form
  - full add/edit lifecycle for Plone content forms.
  - optional immediate content create feature on add


Functionality
=============


Resources Integration with GenericSetup
---------------------------------------

Addon widgets may provide custom javascripts, CSS, images and so on.

This package registers the directories containing these assets as resource directories.
Thus they can be accessed from the webbrowser.
The registration schema is ``++resource++MODULENAME/...``.

The "YAFOWIL Form Library" GenericSetup profile registers all resources related to so called "resource groups" in the CSS and Javascript registries.

**This resource groups must be enabled explicitly(!).**
The resource groups configuration happens via the portal registry.

You need to provide a Generic setup profile containing a ``registry.xml`` with the resource groups configuration, e.g.:

.. code:: XML

    <!-- yafowil.widget.array -->
    <record name="yafowil.widget.array.common">
      <field type="plone.registry.field.Bool">
        <title>Array widget common resources</title>
      </field>
      <value>True</value>
    </record>

The record ``name`` maps to the YAFOWIL resource group name.

Take a look into ``registry.xml`` of the ``yafowil.plone:profiles/demoresources`` profile for more examples.

The YAFOWIL autoform profile registers a bunch of addons and may be used a a reference.


Integration with Translation
----------------------------

The package adds an translation method for Zope2 i18n messages.
It's added using by defining a global preprocessor


Request wrapper
---------------

This package registers a global preprocessor for YAFOWIL.
It wraps the Zope2 request by an own request instance providing the behavior expected by YAFOWIL.

File Uploads provided by Zope2 as ``ZPublisher.HTTPRequest.Fileupload`` objects are turned into a python ``dict`` with the keys:

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
    does not define a ```__call__``` method: define a template in ZCML or a     ```__call__``` method. It provides a method named ```render_form``` which processes and renders the form.

**yafowil.plone.form.Form**
    renders the naked form on ``__call__``.

**yafowil.plone.form.YAMLBaseForm**
    similar to ``BaseForm`` above.
    Expects properties ``form_template`` pointing to a YAML file and ``message_factory`` providing the message factory used for YAML message strings.

**yafowil.plone.form.YAMLForm**
    similar to ``YAMLBaseForm`` renders the naked YAML form on ``__call__``.

An in practice implementation may look like:

.. code:: python

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

Convenience code for creating YAML forms:

.. code:: python

    >>> from zope.i18nmessageid import MessageFactory
    >>> from yafowil.plone.form import YAMLBaseForm

    >>> class MyYAMLForm(YAMLBaseForm):
    ...     action_resource = '@@view_name_callable_by_browser'
    ...     form_template = 'package.name:forms/myform.yaml'
    ...     message_factory = MessageFactory('package.name')

Form classes inherit from ``Products.Five.BrowserPage``, thus they
must be registered via ZCML ``browser:page`` directive:

.. code:: XML

    <browser:page
      for="*"
      name="form_registration_name"
      class=".forms.MyYAMLForm"
      template="myyamlform.pt"
      permission="cmf.ModifyPortalContent"
    />

Forms build with this base form classes need a template in
order to insert such a form in a layout. It must be called inside a
wrapper template ```myform.yaml```:

.. code:: XML

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


When not using one of the BaseForms, the **CSS/JS resources for YAFOWIL are not loaded** automatically.

Add the following lines in order to load it:

.. code:: Python

    from Products.CMFPlone.resources import add_bundle_on_request

    ...

    class MyViewWithYafowil(BrowserView):

    def __init__(self, context, request):
        super(MyViewWithYafowil, self).__init__(context, request)
        add_bundle_on_request(request, 'yafowil')

Autoform
========

**EXPERIMENTAL**:
Autoform features are not feature complete yet and can be considered as *late alpha/early beta* in YAFOWL 4.x.
We plan to move it to a stable state in the 4.x series.
With lots of care, it can be used in production.

YAFOWIL can be used as an drop-in replacement for the ``z3c.form`` based and ``plone.autoform`` generated forms.

Installation
------------

There is a profile called *YAFOWIL Autoform* (in XML: ``yafowil.plone:autoform``).
By installing the profile, all needed to enable YAFOWIL rendered forms is installed.
To finally activate autoform rendering for a content-type, one of the provided YAFOWIL Autoform behaviors has to be activated on the content-type.

Basic Functionality
-------------------

YAFOWIL offers a layer to read ``z3c.form`` ``zope.schema`` annotations and build forms from this information.

Furthermore it offers an own ``zope.schema`` annotations named ``factory`` and ``factory_callable`` to build rich custom YAFOWIL forms without any ``z3c.form`` references.

Examples can be found within the `bda.plone.yafowil_autoform_example behavior <https://github.com/bluedynamics/bda.plone.yafowil_autoform_example/blob/master/src/bda/plone/yafowil_autoform_example/behaviors.py>`_


Usage as z3c.form drop-in replacement
-------------------------------------

There are two behaviors available.

``YAFOWIL forms from content-type schemas``
    Basic configuration with almost same behavior as ``z3c.form`` rendered types.
    Main difference: All widgets and processing is done through YAFOWIL.
    Also, a temporary non-persistent add-context is created and used (opposed to the container as add context in Dexterity).

``YAFOWIL forms from content-type schemas with persistent add context``
    Work the same as the basic one above, but a persistent add context is created.
    I.e., this enables users to upload content in a container just created by the add form.
    On cancel the persistent object is removed.
    To enable removal of stalled content (because user closed browser or similar) an index is added to track the state of the content.
    This immediate creation feature is similar to the one in (but completely independent from) the addon ``collective.immediatecreate``.


Detailed Documentation
======================

If you're interested to dig deeper:
The `detailed YAFOWIL documentation <http://yafowil.info>`_ is available.
Read it and learn how to create your example application with YAFOWIL.


Source Code
===========

The sources are in a GIT DVCS with its main branches at `github <http://github.com/bluedynamics/yafowil.plone>`_.

We'd be happy to see many forks and pull-requests to make YAFOWIL even better.


Contributors
============

- Jens W. Klein <jens [at] bluedynamics [dot] com>

- Peter Holzer <hpeter [at] agitator [dot] com>

- Benjamin Stefaner <bs [at] kleinundpartner [dot] at>

- Robert Niederreiter <rnix [at] squarewave [dot] at>
