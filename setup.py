from setuptools import setup, find_packages
from codecs import open
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), 'r', 'utf-8') as f:
    long_description = f.read()

with open(os.path.join(here, 'machine', '__about__.py'), 'r', 'utf-8') as f:
    about = {}
    exec(f.read(), about)

with open(os.path.join(here, 'requirements.txt'), 'r', 'utf-8') as f:
    dependencies = f.read().splitlines()

setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=long_description,
    license=about["__license__"],
    url=about["__uri__"],
    author=about["__author__"],
    author_email=about["__email__"],
    classifiers=[
        "Development Status :: 3 - Alpha"
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only"
        "Topic :: Communications :: Chat,"
        "Topic :: Internet",
        "Topic :: Office/Business"
    ],
    keywords='slack bot framework ai',
    install_requires=dependencies,
    python_requires='~=3.3',
    entry_points={
        'console_scripts': [
            'slack-machine = machine.bin.run:main',
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False
)
