from setuptools import setup, find_packages
import os

version = '1.3'
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
            'Development Status :: 5 - Production/Stable',
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
      url=u'http://packages.python.org/yafowil.plone',
      license='Simplified BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['yafowil'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'Zope2',
          'yafowil>=1.3',
          'yafowil.yaml>=1.0.2',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone

      [yafowil.plugin]
      register = yafowil.plone:register
      """,
)
