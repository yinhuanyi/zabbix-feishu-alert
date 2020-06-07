# coding: utf-8
"""
@Author: Robby
@Module name: message.py
@Create date: 2020-06-06
@Function: 
"""

import json

import requests

from .message_base import FeishuBase



class FeishuMessage(FeishuBase):

    def _get_tenant_access_token(self, app_id, app_secret):
        tokenurl = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        headers = {"Content-Type": "application/json"}
        data = {"app_id": app_id,
                "app_secret": app_secret}
        request = requests.post(url=tokenurl, headers=headers, json=data)
        response = json.loads(request.content)['tenant_access_token']

        return response
