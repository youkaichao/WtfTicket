from django.template.loader import get_template
from django.test import Client
import xml.etree.ElementTree as ET

from django.utils import timezone

from WeChatTicket import settings


class WechatTestClientLib(Client):
    def __init__(self, **defaults):
        super().__init__(**defaults)
        settings.IGNORE_WECHAT_SIGNATURE = True

    def mock_timezone_now(self, time):
        timezone.now = lambda: time

    def send_text(self, text, open_id):
        resp = self.post('/wechat', data=get_template('user_text.xml').render({
            'ToUserName': '',
            'FromUserName': open_id,
            'Content': text
        }), content_type='text/xml')
        return resp

    def get_text(self, resp):
        root = ET.fromstring(str(resp.content, encoding='utf-8'))
        text_root = root.find('Content')
        if text_root is None:
            return ''
        return text_root.text

    def send_click(self, event_key, open_id):
        resp = self.post('/wechat', data=get_template('user_click.xml').render({
            'ToUserName': '',
            'FromUserName': open_id,
            'EventKey': event_key
        }), content_type='text/xml')
        return resp

    def get_news(self, resp):
        root = ET.fromstring(str(resp.content, encoding='utf-8'))
        articles_root = root.find('Articles')
        news = []
        if articles_root is None:
            return news
        for article in articles_root:
            msg = {}
            for child in article:
                msg[child.tag] = child.text
            news.append(msg)
        return news

    def get_msg_type(self, resp):
        root = ET.fromstring(str(resp.content, encoding='utf-8'))
        msg_type_root = root.find('MsgType')
        if msg_type_root is None:
            return ''
        return msg_type_root.text
