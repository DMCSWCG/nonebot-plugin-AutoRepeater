from setuptools import setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="nonebot_plugin_AutoRepeater",
    version="0.1.0",
    author="DMCSWCG",
    description="A plugin based on NoneBot2, auto repeater message in group.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DMCSWCG/nonebot-plugin-AutoRepeater",
    project_urls={
        "Bug Tracker": "https://github.com/DMCSWCG/nonebot-plugin-AutoRepeater/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=["nonebot_plugin_AutoRepeater"],
    python_requires=">=3.7",
    install_requires=[
        "nonebot2 >=2.0.0rc1",
        "nonebot-adapter-onebot >= 2.0.0rc1"
    ]
)