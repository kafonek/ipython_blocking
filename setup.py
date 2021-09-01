from setuptools import find_packages, setup

setup(
    name="ipython_blocking",
    version="0.3.1",
    author="Matt Kafonek",
    author_email="kafonek@gmail.com",
    url="https://github.com/kafonek/ipython_blocking",
    description="Context manager for blocking cell execution within a Jupyter notebook",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["IPython", "ipywidgets", "nbclient"],
    classifiers=[
        "Framework :: IPython",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
    ],
    license="BSD",
)
