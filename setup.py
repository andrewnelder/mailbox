from setuptools import setup
import os

version = '0.3.4'


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name='alphamail',
    version=version,
    description="Python IMAP for Humans",
    long_description= read('README.md'),
    keywords='email, IMAP, parsing emails',
    author='Martin Rusev',
    author_email='martinrusev@live.com',
    url='https://github.com/andrewnelder/mailbox',
    license='MIT',
    packages=['alphamail'],
    package_dir={'alphamail':'alphamail'},
    zip_safe=False,
    install_requires=[],
) 