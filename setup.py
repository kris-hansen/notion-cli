from setuptools import find_packages
from setuptools import setup

setup(
    packages=find_packages(),
    include_package_data=True,
    entry_points=dict(console_scripts=["notion=notioncli.cli:main"]),
)
