from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tabula-cloud-sync",
    version="1.0.0",
    author="Ysidro Denis",
    author_email="contacto@tabula.com.py",
    description="Servicio de sincronización para Tabula Cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ysidromdenis/template-sync-tabula-cloud",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "configparser>=5.0.0",
    ],
    extras_require={
        "windows": [
            "pywin32>=227; sys_platform == 'win32'",
        ],
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
        ],
        "build": [
            "pyinstaller>=5.0.0",
            "auto-py-to-exe>=2.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tabula-service=service.manager:main",
        ],
    },
    include_package_data=True,
    package_data={
        "icons": ["*.ico"],
        "": ["*.template"],
    },
)
