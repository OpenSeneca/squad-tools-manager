from setuptools import setup, find_packages

setup(
    name="squad-tools-manager",
    version="1.0.0",
    description="Unified CLI wrapper for all OpenSeneca squad tools",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="OpenSeneca Squad",
    author_email="contact@openseneca.org",
    url="https://github.com/OpenSeneca/squad-tools-manager",
    packages=find_packages(),
    py_modules=["main"],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Systems Administration",
    ],
    entry_points={
        "console_scripts": [
            "squad-tools-manager=main:main",
        ],
    },
    keywords="squad tools management cli",
    project_urls={
        "Bug Reports": "https://github.com/OpenSeneca/squad-tools-manager/issues",
        "Source": "https://github.com/OpenSeneca/squad-tools-manager",
    },
)
