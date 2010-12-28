This is the **Zope2 integration for `YAFOWIL 
<http://pypi.python.org/pypi/yafowil>`_** - Yet Another Form WIdget Library.

This package registers a global preprocessor for YAFOWIL. It
 
- wraps the Zope2 request by an own request instance providing the behavior 
  expected by YAFOWIL, and
  
- registers an translation method for Zope2 i18n messages.

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
      
- Due to support of Zope below 2.12 (tested with 2.10) this package does not 
  depend on the Zope2 package. Please provide the packages yourself in your 
  specific setup. At some time we will stop supporting Zope<2.12.      
      
Source Code
===========

The sources are in a GIT DVCS with its main branches at 
`github <http://github.com/bluedynamics/yafowil.zope2>`_.

We'd be happy to see many forks and pull-requests to make YAFOWIL even better.

Contributors
============

- Jens W. Klein <jens@bluedynamics.com> - maintainer