from setuptools import setup, find_packages
import os

version = '0.2.dev0'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='imio.urban.dataimport',
      version=version,
      description="Framework to import external legacy into urban",
      long_description=long_description,
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='IMIO',
      author_email='dev@imio.be',
      url='http://svn.plone.org/svn/collective/',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['imio', 'imio.urban'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.urban'
      ],
      extras_require={'test': ['zope.testing', 'plone.testing', 'plone.app.testing']},
      )
