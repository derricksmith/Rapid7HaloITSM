from setuptools import setup, find_packages

setup(
    name="komand_haloitsm",
    version="1.0.6",
    description="HaloITSM plugin for Rapid7 InsightConnect",
    author="derricksmith",
    packages=find_packages(),
    install_requires=[
        "insightconnect-plugin-runtime>=5.0.0",
        "requests>=2.25.1"
    ],
    scripts=['bin/komand_haloitsm']
)