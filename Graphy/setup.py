from os.path import dirname, abspath, join
from subprocess import call

from setuptools import setup, find_packages, Command

from graphy import __version__

this_dir = abspath(dirname(__file__))

# Readme
with open(join(this_dir, 'README.md'), encoding='utf-8') as file:
    readme = file.read()

# License
with open(join(this_dir, 'LICENSE'), encoding='utf-8') as file:
    license = file.read()

# Requirements
with open(join(this_dir, 'requirements.txt')) as file:
    requirements = file.read().splitlines()


class RunTests(Command):
    """Run all tests."""
    description = 'run tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Run all tests!"""
        error = call(['py.test', '--cov=graphy', '--cov-report=term-missing'])
        raise SystemExit(error)


setup(
    name='graphy',
    version=__version__,
    description='A system monitor command line program in Python.',
    long_description=readme,
    author='André Bento',
    author_email='apbento@student.dei.uc.pt',
    url='https://github.com/...',
    license=license,
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
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
    cmdclass={'test': RunTests},
)
