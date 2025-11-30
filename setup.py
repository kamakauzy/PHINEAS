from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="phineas-osint",
    version="1.0.0",
    author="PHINEAS Team",
    description="Profound HUMINT Intelligence Network & Enrichment Automated System - Comprehensive OSINT automation framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/phineas-osint",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'phineas=phineas:cli',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.yaml', '*.yml', '*.json'],
    },
    keywords='osint intelligence reconnaissance security infosec cybersecurity',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/phineas-osint/issues',
        'Source': 'https://github.com/yourusername/phineas-osint',
        'Documentation': 'https://github.com/yourusername/phineas-osint/blob/main/README.md',
    },
)
