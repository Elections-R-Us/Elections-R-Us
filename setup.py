import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
# with open(os.path.join(here, 'README.md')) as f:
#     README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_jinja2',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',

    'google-api-python-client',
    'psycopg2',
    'passlib',
    ]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',  # includes virtualenv
    'pytest-cov',
    'pytest-watch',
    'tox',
    ]

setup(name='Elections-R-Us',
      version='0.0',
      description='Elections-R-Us',
      # long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'testing': tests_require,
      },
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = elections_r_us:main
      [console_scripts]
      init_db = elections_r_us.scripts.initializedb:main
      """,
      )
