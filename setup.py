from setuptools import setup, find_packages
import os

packages = ['spatialcitizenscience']

install_requires = """
flask>=2.0.0
bleach>=4.0.0
markdown>=3.3.0
Flask-WTF>=1.0.0
geojson
pyyaml
""".split('\n')


def get_version(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), 'r') as fp:
        for line in fp:
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
        else:
            raise RuntimeError("Unable to find version string.")


setup(
    name=packages[0],
    packages=find_packages(),
    version=get_version(packages[0] + '/__init__.py'),
    include_package_data=True,
    install_requires=install_requires,
    python_requires='>=3.8',
    description='SpatialCitizenScience: A simple web app to enable spatial data collection for citizens',
    long_description=open('readme.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jlu-ilr-hydro/spatialcitizenscience',
    author='Philipp Kraft',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: 3 :: Only',
    ],

)