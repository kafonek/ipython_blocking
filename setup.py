import os
from setuptools import setup

def read(fname):
    "Utility function to read the README file.  Used for the long_description."
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()
    
setup(
    name = 'ipython_blocking',
    version = '0.1.0',
    author = 'Matt Kafonek',
    author_email = 'kafonek@gmail.com',
    description = 'Context manager and magic for capturing cell execution in IPython',
    long_description = read('README.md'),
    py_modules = ['ipython_blocking'],
    license = 'BSD',
    keywords = 'IPython blocking',
    url = 'https://github.com/kafonek/ipython_blocking',
    classifiers = [
        'Framework :: IPython',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
    ],
    setup_requires = ['IPython'],
)

