from setuptools import setup

setup(
    name="fastgrpah",
    packages=[
        "fastgraph",
    ],
    include_package_data=True,
    license="MIT",
    description="Fast graph drawing and editing",
    long_description="",
    author="Dmitry Murashov",
    setup_requires=["wheel"],
    install_requires=[
        "tired @ git+https://github.com/damurashov/tired.git@master",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Inependent",
    ],
    python_requires=">=3.7",
    version="0.0.3",
)

