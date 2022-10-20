import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pleasant_promises",
    version="1.1",
    author="AlexCLeduc",
    # author_email="author@example.com",
    # description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlexCLeduc/pleasant-python-promises",
    packages=[
        package
        for package in setuptools.find_packages()
        if package.startswith("pleasant_promises")
        # find_packages() also includes extraneous directories 
    ],
    install_requires=[],
    tests_require=["django"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
