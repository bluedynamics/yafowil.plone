
History
=======

2.2 (2015-10-10)
----------------

- Use ``pkg_resources.get_distribution`` instead of catching ``ImportError``
  to check whether TinyMCE is installed.
  [rnix]

- Make dependency on Products.TinyMCE a soft dependency.
  [thet]


2.1 (2013-06-03)
----------------

- Set applyPrefix for CSS resources to True, so that referenced images can
  still be found.
  [thet, 2014-05-06]

- Integrate translations.
  [rnix, 2014-05-01]


2.0.2
-----

- fix resource group names
  [thet]

- correct getSite import, cleanup
  [thet]

2.0.1
-----

- Provdide default ``title`` attribute value for ``richtext`` blueprint of
  ``yafowil.widget.richtext`` addon widget in order to provide ``TinyMCE``
  configuration as expected by plone integration.
  [rnix]

2.0
---

- YAFOWIL resource including configuration via generic setup.
  [rnix, 2012-10-03]

1.3.1
-----

- Simplify base forms for plone.
  [jensens, 2012-05-21]

- Not ZIP safe!
  [jensens, 2012-04-15]

1.3
---

- GS profile marker - fix wrong filename.
  [rnix, 2012-04-11]

- Add ``yafowil.plone.form`` module containing base classes.
  [rnix, 2012-04-11]


1.2
---

- Rename to yafowil.plone - seems a 2 at the end of a package name confuses
  easy_install. wtf!?
  [jensens, 2012-03-20]


1.1
---

- Depend on yafowil 1.3 in setup.py and bump version.
  [jensens, 2012-03-20]


1.0
---

- Resources are registered using the new plugin infrastructure.
  Theres now an import step for generic setup registering all javascripts and
  stylesheets provided by the plugins. They are registred without any
  thirdparty dependencies. If a resource is already registered its registration
  is skipped. Such its possible to register or overide the defaults using xml
  files.
  [jensens, 2012-02-01]

- Automatic browserresources for plugins.
  [jensens, 2012-02-16]

- Depends on yafowil 1.3 plugin infrastucture.
  [jensens, 2012-02-15]

- Example form and senseful default-classes and plans for plone.
  [hpeter, bennyboy, 2012-02-15]


1.0-beta
--------

- Made it work.
  [jensens, rnix, et al, 2010-12-27]
