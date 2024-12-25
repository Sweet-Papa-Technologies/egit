"""
Setup script for eGit
"""
from setuptools import setup, find_packages

setup(
    name="egit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "litellm>=1.0.0",
        "gitpython>=3.1.40",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "rich>=13.7.0",
        "typer>=0.9.0",
        "click>=8.1.0",
        "platformdirs>=4.1.0",
        "sqlalchemy>=2.0.0"
    ],
    entry_points={
        "console_scripts": [
            "egit=egit.cli:app",
        ],
    },
    author="Forrester Terry",
    author_email="fterry@sweetpapatechnologies.com",
    description="Enhanced Git CLI with LLM capabilities",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Sweet-Papa-Technologies/egit",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
