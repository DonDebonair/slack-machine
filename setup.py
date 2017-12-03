from codecs import open
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), 'r', 'utf-8') as f:
    long_description = f.read()

with open(os.path.join(here, 'machine', '__about__.py'), 'r', 'utf-8') as f:
    about = {}
    exec(f.read(), about)

with open(os.path.join(here, 'requirements.txt'), 'r', 'utf-8') as f:
    dependencies = f.read().splitlines()


class PublishCommand(Command):
    """
    Support setup.py publish.
    Graciously taken from https://github.com/kennethreitz/setup.py
    """

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def _remove_builds(self, msg):
        try:
            self.status(msg)
            rmtree(os.path.join(here, 'dist'))
            rmtree(os.path.join(here, 'build'))
            rmtree(os.path.join(here, '.egg'))
            rmtree(os.path.join(here, 'slack_machine.egg-info'))
        except FileNotFoundError:
            pass

    def run(self):
        try:
            self._remove_builds("Removing previous builds…")
        except FileNotFoundError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable))

        self.status("Uploading the package to PyPi via Twine…")
        os.system('twine upload dist/*')

        self._remove_builds("Removing builds…")

        sys.exit()


setup(
    name=about["__title__"],
    version=about["__version__"],
    description=about["__description__"],
    long_description=long_description,
    license=about["__license__"],
    url=about["__uri__"],
    author=about["__author__"],
    author_email=about["__email__"],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov', 'coverage'],
    install_requires=dependencies,
    python_requires='~=3.3',
    extras_require={
        'redis': ['redis', 'hiredis']
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Communications :: Chat",
        "Topic :: Internet",
        "Topic :: Office/Business"
    ],
    keywords='slack bot framework ai',
    entry_points={
        'console_scripts': [
            'slack-machine = machine.bin.run:main',
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    cmdclass={
        'publish': PublishCommand,
    }
)
