"""
    Author: André Bento
    Date last modified: 20-02-2019
"""
import subprocess
from os.path import dirname, abspath, join

from setuptools import find_packages, Command, setup

this_dir = abspath(dirname(__file__))

NAME = 'graphy'
VERSION = '0.0.1'

# Readme
with open(join(this_dir, 'README.md'), encoding='utf-8') as file:
    readme = file.read()

# License
with open(join(this_dir, 'LICENSE'), encoding='utf-8') as file:
    license_file = file.read()

# Requirements
with open(join(this_dir, 'requirements.txt')) as file:
    requirements = file.read().splitlines()


class InstallCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        commands = [
            ['./scripts/create-directories.sh'],
            ['pip3', 'install', '-r', 'requirements.txt']
        ]
        for command in commands:
            subprocess.run(command)


class RunCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from graphy.app import Graphy
        Graphy.run()


class TestCommand(Command):
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print('Hello')
        """Run all tests!"""
        # error = call(['py.test', '--cov=graphy', '--cov-report=term-missing'])
        # raise SystemExit(error)
        pass


setup(
    name=NAME,
    version=VERSION,
    description='A micro-services system monitor command line program in Python.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/andrepbento/MScThesis/tree/master/Graphy',
    author='André Bento',
    author_email='apbento@student.dei.uc.pt',
    license=license_file,
    classifiers=[
        # How mature is this project? Common values are
        #   1 - Project setup
        #   2 - Prototype
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 2 - Prototype',
        'Intended Audience :: Developers',
        'Topic :: Observing and Controlling Performance in  Micro-services',
        'License :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='cli',
    packages=find_packages(exclude=('tests*', 'docs')),
    install_requires=requirements,
    extras_require={
        'test': ['coverage', 'pytest', 'pytest-cov'],
    },
    entry_points={
        'console_scripts': [
            'graphy=graphy.cli:cli',
        ],
    },
    cmdclass={
        'install': InstallCommand,
        'run': RunCommand,
        'test': TestCommand
    },
)
