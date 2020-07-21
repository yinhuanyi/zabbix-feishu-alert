# coding: utf-8
"""
@Author: Robby
@Module name: setup.py
@Create date: 2020-06-06
@Function: 
"""

import os
from setuptools import setup

def package_data(pkg, roots=tuple()):
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                print(os.path.relpath(os.path.join(dirname, fname), pkg))
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}

with open("README.md", "r") as f:
  long_description = f.read()

setup(
    name = 'zabbix-feishu-alert',
    author = 'Robby',
    author_email = 'yinhuanyicn@gmail.com',
    url = 'https://github.com/yinhuanyi/zabbix-feishu-alert',
    license = "MIT",
    version = '1.0.8',
    description = 'zabbix send alert message and graph to feishu robot',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = [
        'zabbix_feishu_alert',
    ],
    install_requires = [
        'requests',
    ],
    dependency_links = [],
    package_data = package_data("zabbix_feishu_alert",),
)