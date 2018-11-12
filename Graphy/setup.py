from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='graphy',
    version='0.1.0',
    description='',
    long_description=readme,
    author='André Bento',
    author_email='apbento@student.dei.uc.pt',
    url='https://github.com/...',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
