from setuptools import setup, find_packages

setup(
    name="komand_haloitsm",
    version="1.0.1",
    description="HaloITSM plugin for Rapid7 InsightConnect",
    author="Rapid7",
    packages=find_packages(),
    install_requires=[
        "insightconnect-plugin-runtime>=5.0.0",
        "requests>=2.25.1"
    ],
    entry_points={
        "console_scripts": [
            "komand_haloitsm = komand_haloitsm.bin.komand_haloitsm:main"
        ]
    }
)