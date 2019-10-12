"""
Setup to install kube-shodan as a Python package.
"""

from datetime import datetime
from os import getenv
from setuptools import find_packages, setup


def readme():
    """
    Read the full README.md file as a string.
    """
    with open('README.md') as file_read:
        return file_read.read()


setup(
    name='kube-shodan',
    version=getenv('GITHUB_REF',
                   default=datetime.now().strftime('%Y.%m.%d.dev%H%M%S')).lstrip('refs/tags/'),
    description='kube-shodan registers all public IPs of a Kubernetes '
                'cluster to monitor.shodan.io.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/ekeih/kube-shodan',
    author='Max Rosin',
    author_email='kube-shodan@hackrid.de',
    license='GPL',
    classifiers=[
        'Programming Language :: Python :: 3'
    ],
    python_requires='>=3.7',
    install_requires=['click', 'kubernetes', 'shodan'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'kube-shodan=kubeshodan.main:main'
        ]
    }
)
