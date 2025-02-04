from mochi import GE_PYTHON_34, __author__, __license__, __version__
from pip.download import PipSession
from pip.req import parse_requirements
from setuptools import find_packages, setup

install_reqs = parse_requirements("requirements.txt", session=PipSession())
install_requires = [str(ir.req) for ir in install_reqs]

if not GE_PYTHON_34:
    install_requires.append("pathlib>=1.0.1")


def is_windows():
    from sys import platform

    return platform.startswith("win") or platform.startswith("cygwin")


if is_windows():
    readme = ""
else:
    with open("README.rst", "r") as f:
        readme = f.read()

setup(
    name="mochi",
    version=__version__,
    description="Dynamically typed functional programming language",
    long_description=readme,
    license=__license__,
    author=__author__,
    url="https://github.com/i2y/mochi",
    platforms=["any"],
    entry_points={"console_scripts": ["mochi = mochi.core:main"]},
    packages=find_packages(),
    package_data={
        "mochi": [
            "sexpressions/*",
            "core/import_global_env.mochi",
            "core/import_global_env_and_monkey_patch.mochi",
        ],
    },
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Compilers",
    ],
)
