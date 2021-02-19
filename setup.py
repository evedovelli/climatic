import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="climate",
    version="0.0.1",
    author="Estevan Vedovelli",
    author_email="evedovelli@gmail.com",
    description="Tool to ease and automate CLI usage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/evedovelli/climate",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
