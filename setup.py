"""mqtt_base setup.py."""

import setuptools
from mqtt_base.const import APP_NAME, VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=APP_NAME,
    version=VERSION,
    author="Crowbar Z",
    author_email="crowbarz@outlook.com",
    description="Event driven base framework for MQTT applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/crowbarz/mqtt-base",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
    ],
    python_requires=">=3.9",
    install_requires=[
        "python-daemon==3.0.1",
        "paho-mqtt==1.6.1",
    ],
    entry_points={
        "console_scripts": [
            "mqtt-base=mqtt_base.mqtt_base:main",
        ]
    },
)
