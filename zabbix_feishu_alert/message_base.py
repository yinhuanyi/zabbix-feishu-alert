# coding: utf-8
"""
@Author: Robby
@Module name: message_base.py
@Create date: 2020-06-06
@Function: 
"""

import os
import json
from datetime import datetime

import requests
from requests.cookies import RequestsCookieJar


class FeishuBase:

    def __init__(self, zabbix_host, zabbix_user, zabbix_passwd, user_mobile, item_id, data_dir, app_id, app_secret):
        """

        :param zabbix_host: zabbix ip address
        :param zabbix_user: zabbix admin username
        :param zabbix_passwd: zabbix admin passwd
        :param user_mobile: people mobile
        :param item_id: zabbix item id
        :param data_dir: zabbix graph storage directory
        """

        self.tenant_access_token = self._get_tenant_access_token(app_id, app_secret)
        self.chat_id = self._get_chat_id(self.tenant_access_token)
        self.user_id = self._get_user_id(self.tenant_access_token, user_mobile)
        self.zabbix_graph = self._get_zabbix_graph(item_id, zabbix_host, zabbix_user, zabbix_passwd, data_dir)
        self.image_key = self._upload_zabbix_graph(self.tenant_access_token, self.zabbix_graph)

    def _get_tenant_access_token(self, *args, **kwargs):
        raise Exception("Please Implement This Method")

    def _get_user_id(self, tenant_access_token, user_mobile):
        """

        :param tenant_access_token: feishu tenant_access_token
        :param user_mobile: people mobile
        :return: user id
        """
        mobiles = user_mobile
        userurl = "https://open.feishu.cn/open-apis/user/v1/batch_get_id?mobiles=%s" % mobiles
        headers = {"Authorization": "Bearer %s" % tenant_access_token}
        request = requests.get(url=userurl, headers=headers)
        response = json.loads(request.content)['data']['mobile_users'][mobiles][0]['user_id']
        return response

    def _get_chat_id(self, tenant_access_token):
        """

        :param tenant_access_token: feishu tenant_access_token
        :return: chat id
        """
        chaturl = "https://open.feishu.cn/open-apis/chat/v4/list?page_size=20"
        headers = {"Authorization": "Bearer %s" % tenant_access_token, "Content-Type": "application/json"}
        request = requests.get(url=chaturl, headers=headers)
        response = json.loads(request.content)['data']['groups'][0]['chat_id']
        return response

    def _get_zabbix_graph(self, item_id, zabbix_host, zabbix_user, zabbix_passwd, data_dir):
        """

        :param item_id: zabbix item id
        :param zabbix_host: zabbix ip addr
        :param zabbix_user: zabbix admin username
        :param zabbix_passwd: zabbix admin passwd
        :param data_dir: zabbix graph storage directory
        :return: local absolute zabbix graph path name
        """
        # 创建session会话
        session = requests.Session()

        # 定义session头部
        loginheaders = {
            "Host": zabbix_host,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
            'Referer': 'http://{}/zabbix/index.php'.format(zabbix_host)
        }

        # 定义payload
        payload = {
            "name": zabbix_user,
            "password": zabbix_passwd,
            "autologin": 1,
            "enter": "Sign in",
        }

        try:
            # session登录
            login_ret = session.post(url='http://{}/zabbix/index.php'.format(zabbix_host),
                                     headers=loginheaders,
                                     data=payload)
            # 获取cookie
            cookies = login_ret.cookies

            # 初始化jar，写入cookie
            jar = RequestsCookieJar()
            for item in cookies.iteritems():
                jar.set(item[0], item[1], domain='{}'.format(zabbix_host), path='/zabbix')

            # 访问图标
            graph_response = requests.get('http://{}/zabbix/chart.php?period=7200&width=600&time=600&itemids={}'.format(zabbix_host, item_id),cookies=jar)

            # 拼接图片路径
            local_time_str = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
            graph_name = 'zabbix_' + local_time_str + '.png'

            graph_path = os.path.join(data_dir, graph_name)

            # 使用绝对路径保存图片，二进制写入
            with open(graph_path, 'wb', ) as f:
                f.write(graph_response.content)

            # 返回图片名称
            return graph_path

        except Exception:
            raise Exception("get zabbix graph failed")

    def _upload_zabbix_graph(self, tenant_access_token, graph_path):
        """

        :param tenant_access_token: feishu tenant_access_token
        :param graph_path: local absolute zabbix graph path name
        :return:
        """
        with open(graph_path, 'rb') as f:
            image = f.read()

        img_url = 'https://open.feishu.cn/open-apis/image/v4/put/'
        headers = {'Authorization': "Bearer %s" % tenant_access_token}
        files = {"image": image}
        data = {"image_type": "message"}
        resp = requests.post(
            url=img_url,
            headers=headers,
            files=files,
            data=data
        )
        resp.raise_for_status()
        content = resp.json()

        # 获取上传的image_key
        return content['data']['image_key']

    # 发送告警消息
    def send_alarm_message(self, title, content, event_id, zabbix_ack_addr):
        """

        :param user_id: user id
        :param chat_id: chat id
        :param tenant_access_token: feishu tenant_access_token
        :param image_key: feishu image key
        :param title: zabbix alart title
        :param content: zabbix alart content
        :param event_id: zabbix event id
        :param zabbix_ack_addr: your website for zabbix alert ack addr
        :return: None
        """

        send_url = "https://open.feishu.cn/open-apis/message/v4/send/"
        headers = {"Authorization": "Bearer %s" % self.tenant_access_token, "Content-Type": "application/json"}
        data = {
            "chat_id": self.chat_id,
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "un_escape": True,
                                    "text": content
                                },
                                {
                                    "tag": "at",
                                    "user_id": self.user_id

                                },
                                {
                                    "tag": "a",
                                    "text": "\n立即处理",
                                    # http://{}:8000/monitor/problem_ack/
                                    "href": "{}?event_id={}".format(zabbix_ack_addr, event_id)
                                },
                            ],
                            [
                                {
                                    "tag": "img",
                                    "image_key": self.image_key,
                                    "width": 1000,
                                    "height": 600
                                }
                            ]
                        ]
                    }
                }
            }
        }

        requests.post(url=send_url, headers=headers, json=data)

    # 发送恢复消息
    def send_recovery_message(self, title, content):

        """
        :param title: zabbix alert title
        :param content: zabbix alert content
        :return: None
        """
        sendurl = "https://open.feishu.cn/open-apis/message/v4/send/"
        headers = {"Authorization": "Bearer %s" % self.tenant_access_token, "Content-Type": "application/json"}
        data = {
            "chat_id": self.chat_id,
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "un_escape": True,
                                    "text": content
                                },
                                {
                                    "tag": "at",
                                    "user_id": self.user_id

                                },
                            ],
                            [
                                {
                                    "tag": "img",
                                    "image_key": self.image_key,
                                    "width": 1000,
                                    "height": 600
                                }
                            ]
                        ]
                    }
                }
            }
        }
        requests.post(url=sendurl, headers=headers, json=data)

    # 发送确认消息
    def send_ack_message(self, title, content):
        """

        :param title: zabbix alert title
        :param content: zabbix alert content
        :return: None
        """
        sendurl = "https://open.feishu.cn/open-apis/message/v4/send/"
        headers = {"Authorization": "Bearer %s" % self.tenant_access_token, "Content-Type": "application/json"}
        data = {
            "chat_id": self.chat_id,
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "un_escape": True,
                                    "text": content
                                },
                                {
                                    "tag": "at",
                                    "user_id": self.user_id
                                },
                            ],
                            [
                                {
                                    "tag": "img",
                                    "image_key": self.image_key,
                                    "width": 1000,
                                    "height": 600
                                }
                            ]
                        ]
                    }
                }
            }
        }
        requests.post(url=sendurl, headers=headers, json=data)
