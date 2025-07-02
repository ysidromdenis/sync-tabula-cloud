from setuptools import find_packages, setup
from setuptools.command.develop import develop
from setuptools.command.install import install

# Importar build tools solo si están disponibles
try:
    from tabula_cloud_sync.build_tools.post_install import PostInstallHooks

    HOOKS_AVAILABLE = True
except ImportError:
    HOOKS_AVAILABLE = False


class PostInstallCommand(install):
    """Custom post-installation for install mode."""

    def run(self):
        install.run(self)
        if HOOKS_AVAILABLE:
            try:
                PostInstallHooks.run_post_install()
            except Exception as e:
                print(f"Warning: Post-install hooks failed: {e}")


class PostDevelopCommand(develop):
    """Custom post-installation for development mode."""

    def run(self):
        develop.run(self)
        if HOOKS_AVAILABLE:
            try:
                PostInstallHooks.run_post_install()
            except Exception as e:
                print(f"Warning: Post-install hooks failed: {e}")


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tabula-cloud-sync",
    version="1.0.0",
    author="Ysidro Denis",
    author_email="contacto@tabula.com.py",
    description="Librería reutilizable para sincronización con Tabula Cloud",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ysidromdenis/sync-tabula-cloud",
    packages=find_packages(
        include=["tabula_cloud_sync", "tabula_cloud_sync.*"]
    ),
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
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Database :: Database Engines/Servers",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=2.11.7",
        "configparser>=5.0.0",
        "pyyaml>=6.0",
        "click>=8.0.0",
        "platformdirs>=4.3.8",
    ],
    extras_require={
        "windows": [
            "pywin32>=227; sys_platform == 'win32'",
        ],
        "database": [
            # "psycopg2-binary>=2.9.0",
            "mysql-connector-python>=9.3.0",
            # "pymssql>=2.2.0",
            # "pymongo>=4.0.0",
        ],
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.910",
        ],
        "build": [
            "pyinstaller>=5.0.0",
            "auto-py-to-exe>=2.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tabula-service=tabula_cloud_sync.service.manager:main",
            "tabula-cli=tabula_cloud_sync.cli.main:cli",
            "tabula-build=tabula_cloud_sync.build_tools.cli:build_cli",
        ],
    },
    cmdclass={
        "install": PostInstallCommand,
        "develop": PostDevelopCommand,
    },
    include_package_data=True,
    package_data={
        "tabula_cloud_sync": [
            "templates/*",
            "templates/**/*",
            "icons/*.ico",
            "config/*.template",
            "config/*.yaml",
        ],
    },
    zip_safe=False,  # Para permitir acceso a archivos de datos
)
