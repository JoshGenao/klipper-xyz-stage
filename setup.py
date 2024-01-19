import setuptools
setuptools.setup(
    name = "klipperXYZ",
    version = "0.1",
    author = "Josh Genao",
    author_email = "jgenao622@gmail.com",
    description = "A Python interface that simplifies the control of a Klipper programmed 3D printer",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)