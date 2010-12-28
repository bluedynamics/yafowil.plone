from setuptools import setup, find_packages
import os

version = '1.0-beta'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'HISTORY.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()
shortdesc = 'YAFOWIL - Yet Another Form Widget Lib: Integration with Zope 2'
tests_require = ['interlude']

setup(name='yafowil.zope2',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            #'Development Status :: 5 - Production/Stable',
            'Development Status :: 4 - Beta',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Framework :: Zope2',
            'Framework :: Plone',
            'License :: OSI Approved :: BSD License',                        
      ],
      keywords='zope2 request response html input widgets',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'http://packages.python.org/yafowil.zope2',
      license='Simplified BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['yafowil'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          #'Zope2',
          'yafowil',
      ],
      #tests_require=tests_require,
      #test_suite="yafowil.zope2.tests.test_suite",
      #extras_require = dict(
      #    tests=tests_require,
      #),
)
