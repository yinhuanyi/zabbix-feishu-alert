# coding: utf-8
"""
@Author: Robby
@Module name: setup.py
@Create date: 2020-06-06
@Function: 
"""

import os
from setuptools import  setup

def package_data(pkg, roots=tuple()):
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                print(os.path.relpath(os.path.join(dirname, fname), pkg))
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}



setup(
    # 包名称
    name = 'zabbix_feishu_alart',
    # 模块作者
    author = 'Robby',
    # 作者邮件
    author_email = 'yinhuanyicn@gmail.com',
    # 官方站点
    url = 'http://bbs.yhyblog.cn',
    # 模块协议,
    license = "MIT",
    # 包版本
    version = '1.0.0',
    # 包的描述
    description = 'zabbix send alert message and graph to feishu robot',
    packages = [
        'feishu_alert',
    ],
    install_requires = [
        'requests',
    ],
    dependency_links = [],

    package_data = package_data("feishu_alert",),
)