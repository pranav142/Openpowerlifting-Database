from setuptools import setup, find_packages

setup(
    name="data",
    package_dir={"": "src"},
    version="0.1",
    packages=find_packages(where="src"),
    description="Source Code For Open Powerlifting Database",
    author="Pranav Nadimpalli",
    author_email="pknadimp@gmail.com",
)
