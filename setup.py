import setuptools
import sys
import re

VERSIONFILE = "embr_survey/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

with open("readme.md", "r") as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="embr_survey",
    version=verstr,
    install_requires=requirements,
    author="Alex Forrence",
    author_email="alex.forrence@gmail.com",
    description="_",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aforren1/embrwave_multisite",
    packages=setuptools.find_packages(),
    package_data={'embr_survey': ['images/*']},
    python_requires='>=3.7',
    include_package_data=True,
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
