"Setup script"
from setuptools import setup, find_packages


def _requirements():
    with open("requirements.txt") as req_file:
        return req_file.read().splitlines()


def _readme():
    with open('README.md') as readme_file:
        return readme_file.read()


setup(
    name="clang_tidy_converter",
    url="https://github.com/yuriisk/clang-tidy-converter",
    version="1.0.0",
    packages=find_packages(),
    author="Yurii Skatarenko",
    author_email="yurii.skatarenko@gmail.com",
    description="Python3 script to convert Clang-Tidy output to different formats.",
    long_description=_readme(),
    long_description_content_type='text/markdown',
    keywords="",
    license="MIT",
    platforms=["any"],
    python_requires='>=3.5',
    install_requires=_requirements(),
    setup_requires=['pytest-runner', 'wheel'],
    tests_require=['pytest'],
    classifiers=[],
)

