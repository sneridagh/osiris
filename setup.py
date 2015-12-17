import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = ['pyramid',
            'pyramid_debugtoolbar',
            'pyramid_who',
            'pymongo',
            'waitress']

setup(name='osiris',
      version='1.5.7.dev0',
      description='Pyramid based oAuth server',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pylons",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Victor Fernandez de Alba',
      author_email='sneridagh@gmail.com',
      url='https://github.com/sneridagh/osiris.git',
      keywords='web pyramid pylons',
      packages=find_packages('.'),
      package_dir={'': '.'},
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires + ['WebTest', 'WSGIProxy2'],
      extras_require={
          'test': ['WebTest', 'WSGIProxy2', 'pyramid_ldap'],
          'ldap': ['pyramid_ldap', ],
      },
      entry_points="""
      [paste.app_factory]
      main = osiris:make_osiris_app
      """,
      )
