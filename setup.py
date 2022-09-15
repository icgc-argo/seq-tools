#!/usr/bin/env python3

import re
import ast
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('seq_tools/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass into py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

with open('requirements.txt') as f:
    install_reqs = f.read().splitlines()
with open('requirements-test.txt') as f:
    tests_require = f.read().splitlines()


setup(
    name='seq-tools',
    version=version,
    description='Command line tools for ICGC ARGO sequencing data/metadata',
    license='GNU Affero General Public License v3.0',
    url='https://github.com/icgc-argo/seq-tools',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={"":["resources/*/*/refseq.bed","resources/star_chr21_index/*"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    install_requires=install_reqs,
    python_requires='>=3',
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    entry_points={
        'console_scripts': [
            'seq-tools=seq_tools.cli:main',
        ]
    }
)