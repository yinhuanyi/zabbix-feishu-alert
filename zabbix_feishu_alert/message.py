# coding: utf-8
"""
@Author: Robby
@Module name: message.py
@Create date: 2020-06-06
@Function: 
"""

import json

import requests

from zabbix_feishu_alert.message_base import FeishuBase



class FeishuMessage(FeishuBase):

    def _get_tenant_access_token(self, app_id, app_secret):
        tokenurl = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
        headers = {"Content-Type": "application/json"}
        data = {"app_id": app_id,
                "app_secret": app_secret}
        request = requests.post(url=tokenurl, headers=headers, json=data)
        response = json.loads(request.content)['tenant_access_token']

        return response


if __name__ == '__main__':
    feishu = FeishuMessage('10.102.0.4',
                           'Admin',
                           'zabbix',
                           '18670236750',
                           36836,
                           './',
                           'cli_9e44d8e26dbb500d',
                           '8X4jX9MLwg6AXIEVJh0lC8oeHNDBfbnd')

    feishu.send_alarm_message(feishu.user_id,
                              feishu.chat_id,
                              feishu.tenant_access_token,
                              feishu.image_key,
                              "Zabbix Alert Title",
                              "Zabbix Alert Content",
                              38524,
                              '10.102.0.11')
