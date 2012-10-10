from setuptools import setup, find_packages
import os

version = '2.0'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'HISTORY.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()
shortdesc = 'Plone Integration with YAFOWIL'
tests_require = ['interlude']

setup(name='yafowil.plone',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Framework :: Zope2',
            'Framework :: Plone',
            'License :: OSI Approved :: BSD License',
      ],
      keywords='zope2 plone request response html input widgets',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'http://pypi.python.org/pypi/yafowil.plone',
      license='BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['yafowil'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
          'yafowil>1.99',
          'yafowil.yaml>=1.0.2',
      ],
      extras_require={
          'addons': [
              'collective.js.jqueryui',
          ]
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone

      [yafowil.plugin]
      register = yafowil.plone:register
      """,
)
