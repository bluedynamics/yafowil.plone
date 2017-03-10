from setuptools import find_packages
from setuptools import setup
import os


version = '2.4.1'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'CHANGES.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()
shortdesc = 'Plone Integration with YAFOWIL'
tests_require = ['interlude']


setup(
    name='yafowil.plone',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Framework :: Zope2",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
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
        'Products.CMFPlone',
        'yafowil>=2.1.99',
        'yafowil.yaml>=1.0.4',
    ],
    extras_require={
        'addons': [
            'collective.js.jqueryui'
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone

    [yafowil.plugin]
    register = yafowil.plone:register
    configure = yafowil.plone:configure
    """)
