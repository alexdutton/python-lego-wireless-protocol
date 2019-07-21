import setuptools

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="lego-wireless",
    version="0.1",
    description="Control Lego Powered Up devices over Bluetooth",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alexander Dutton",
    author_email="code@alexdutton.co.uk",
    url="https://github.com/alexsdutton/python-lego-wireless-protocol",
    license="MIT",
    packages=setuptools.find_packages(),
    install_requires=["gatt", "blinker"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ],
)
