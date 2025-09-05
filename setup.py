#!/usr/bin/env python3
"""
Setup script for Metisara - JIRA Project Management Automation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read version from package
version = {}
with open("src/metisara/__init__.py") as fp:
    exec(fp.read(), version)

setup(
    name="metisara",
    version=version['__version__'],
    author="Red Hat Product Security",
    author_email="",
    description="JIRA Project Management Automation through CSV processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/metisara",
    project_urls={
        "Bug Reports": "https://github.com/your-org/metisara/issues",
        "Source": "https://github.com/your-org/metisara",
        "Documentation": "https://github.com/your-org/metisara#readme",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Scheduling",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "jira>=3.0.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "metisara=metisara.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "metisara": [
            "examples/*.conf",
        ],
    },
    zip_safe=False,
    keywords="jira project-management automation csv workflow tickets",
)
