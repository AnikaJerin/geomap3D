from setuptools import setup, find_packages

setup(
    name="geomap3D",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "geomap3d": ["templates/*.html"],
    },
    install_requires=[], 
    description="A pure Python library for interactive 3D mapping.",
    author="Syeda Anika Jerin",
)