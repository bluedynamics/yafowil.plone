This is the **Zope2 integration** for `YAFOWIL
<http://pypi.python.org/pypi/yafowil>`_

Functionality
=============

Browser Resources
-----------------

Plugins may provide custom javascript, css, images (and so on). This package
registers the directory containing them as a resource-directory. Thus they can
be accessed from the webbrowser. The schema is
``+++resource++MODULENAME/filename.ext``. I.e. if ``yafowil.widget.autocomplete``
is available its javascript can be accessed with
``http://localhost:8080/Plone/++resource++yafowil.widget.autocomplete/widget.js``.

Integration with Plone and GenericSetup
---------------------------------------

There a profile ``YAFOWIL`` available registering all browser resources in css 
and javascript registries.

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

Source Code
===========

The sources are in a GIT DVCS with its main branches at
`github <http://github.com/bluedynamics/yafowil.zope2>`_.

We'd be happy to see many forks and pull-requests to make YAFOWIL even better.

Contributors
============

- Jens W. Klein <jens@bluedynamics.com> - maintainer

- Peter Holzer <hpeter@agitator.com>

- Benjamin Stefaner <bs@kleinundpartner.at>
