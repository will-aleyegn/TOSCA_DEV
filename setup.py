"""
TOSCA Laser Control System
Setup configuration for package installation and distribution.
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="tosca-laser-control",
    version="0.1.0-alpha",
    author="Aleyegn",
    author_email="",
    description="TOSCA Laser Control System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/will-aleyegn/Aleyegn_TOSCA_Control_Development",
    project_urls={
        "Bug Tracker": ("https://github.com/will-aleyegn/Aleyegn_TOSCA_Control_Development/issues"),
        "Documentation": (
            "https://github.com/will-aleyegn/Aleyegn_TOSCA_Control_Development/tree/main/docs"
        ),
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "License :: Other/Proprietary License",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "PyQt6>=6.6.0",
        "pyqtgraph>=0.13.3",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "pyserial>=3.5",
        "adafruit-blinka>=8.20.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.12.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "jsonschema>=4.19.0",
        "python-dateutil>=2.8.2",
        "loguru>=0.7.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-qt>=4.2.0",
            "pytest-mock>=3.11.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
            "pylint>=2.17.0",
            "safety>=2.3.0",
            "bandit>=1.7.5",
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
            "ipython>=8.14.0",
            "ipdb>=0.13.13",
            "pre-commit>=3.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tosca-control=main:main",
        ],
    },
)
