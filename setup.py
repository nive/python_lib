import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'requests'
    ]

try:
    README = open(os.path.join(here, 'readme.rst')).read()
except:
    README = ''

setup(name='pynive_client',
      version='0.9.1',
      description='nive.io python client library',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "License :: OSI Approved :: BSD License"
        ],
      author='Arndt Droullier, Nive GmbH',
      author_email='info@nive.co',
      url='http://nive.io',
      keywords='nive client libs',
      packages=find_packages(),
      include_package_data=True,
      license='BSD 3',
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="pynive_client"
)

