Introduction
============

This is the Zope2 integration for YAFOWIL - Yet Another Form WIdget Library.

This package registers a global preprocessor for yafowil. It wraps the any Zope2 
Request derived request instance. .

Spezial behaviors: 

BELOW HERE: WRITE ME!!!
     
- File Uploads provided by WebOb as ``cgi.FieldStorage`` objects are turned into 
  Dicts with the keys:
  
  file
      file-like object to read data from
      
  filename
      submitted name of the upload
      
  mimetype
      type of the upload
      
  headers
      all headers 
      
  original
      keeps the original ``cgi.FieldStorage`` object

Changes
=======

1.0 (work in progress)
----------------------

- Initial: Make it work (jensens)

Credits
=======

- Written and concepted by Jens W. Klein <jens@bluedynamics.com>
