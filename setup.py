import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mahjong_api",
    version="1.0.0",
    author="Dustin Axman",
    author_email="dustinaxman@gmail.com",
    description="This package sets up an API for getting the best mahjong move using Deep Reinforcement Learning.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dustinaxman/mahjong_ai_api",
    project_urls={
        "Codebase": "https://github.com/dustinaxman/mahjong_ai_api",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
