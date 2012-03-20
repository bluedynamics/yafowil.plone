
History
=======

1.2
---

- rename to yafowil.plone - seems a 2 at the end of a package name confuses 
  easy_install. wtf!?
  [jensens, 2012-03-20]

1.1
---

- depend on yafowil 1.3 in setup.py and bump version.
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

- automatic browserresources for plugins [jensens, 2012-02-16]

- depends on yafowil 1.3 plugin infrastucture [jensens, 2012-02-15]

- example form and senseful default-classes and plans for plone
  [hpeter, bennyboy, 2012-02-15]

1.0-beta
--------

- made it work [jensens, rnix, et al, 2010-12-27]

