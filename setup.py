# Copyright 2009, BlueDynamics Alliance - http://bluedynamics.com
# Python Software Foundation License

from setuptools import setup, find_packages
import sys, os

version = '1.0'
shortdesc = 'YAFOWIL: Integration with Zope2'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
tests_require = ['interlude']

setup(name='yafowil.zope2',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'License :: OSI Approved :: Python Software Foundation License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development',
      ],
      keywords='zope2 request response html input widgets',
      author='Jens W. Klein',
      author_email='dev@bluedynamics.com',
      url=u'',
      license='Python Software Foundation License',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['yafowil'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          #'Zope2',
          'yafowil',
      ],
      tests_require=tests_require,
      test_suite="yafowil.zope2.tests.test_suite",
      extras_require = dict(
          tests=tests_require,
      ),
)
