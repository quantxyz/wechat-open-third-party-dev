# coding=utf-8
__author__ = 'Jerry'
import json
import time
import requests
from django.shortcuts import get_object_or_404
from .models import Authorization_info
from wxopenserver import WxOpenSDK

class WxOpenClient:
    def __init__(self, authorizer_appid):
        self.authorizer_appid = authorizer_appid

    def getAccessToken(self):
        info = get_object_or_404(Authorization_info,
                                 authorizer_appid=self.authorizer_appid)
        now = time.time()
        if info.token_expires_time < now:
            r_token = info.authorizer_refresh_token
            # load file
            json_file = open('com_ticket.json')
            data = json.load(json_file)
            json_file.close()

            if data['ComponentVerifyTicket'] == '':
                return
            ComponentVerifyTicket = data['ComponentVerifyTicket']
            wxOpenSDK = WxOpenSDK(ticket=ComponentVerifyTicket)
            r_data = wxOpenSDK.get_refresh_authorizer_access_token(authorizer_appid=self.authorizer_appid,
                                                          authorizer_refresh_token=r_token)
            info.authorizer_access_token = r_data['authorizer_access_token']
            info.token_expires_time = int(now)+7000
            info.authorizer_refresh_token = r_data['authorizer_refresh_token']
            info.save()
        return info.authorizer_access_token

    def getTechUsers(self, tag_id):
        url = "https://api.weixin.qq.com/cgi-bin/user/tag/get?access_token=%s" % (self.getAccessToken())
        payload = {'tagid': tag_id, 'next_openid': ''}
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        data = response.json()
        print data
        openids = data['data']['openid']
        return openids

    def getUserInfo(self, openid):
        # https://api.weixin.qq.com/cgi-bin/user/info?access_token=ACCESS_TOKEN&openid=OPENID&lang=zh_CN
        url = "https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN" \
              % (self.getAccessToken(), openid)
        response = requests.get(url)
        return response.json()

    def getQcodeUrl(self, oid):
        url = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token=%s" % (self.getAccessToken())
        payload = {'expire_seconds': 2591999, 'action_name': 'QR_SCENE', 'action_info': {"scene": {"scene_id": oid}}}
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        data = response.json()
        ticket = data['ticket']
        # http://weixin.qq.com/q/zUipXRjlo7zaLJROUmaT
        # print data['url']
        url_qcode = "https://mp.weixin.qq.com/cgi-bin/showqrcode?"
        params = {'ticket': ticket}
        from urllib import urlencode
        # Content-Type:image/jpg
        return url_qcode + urlencode(params)

    def sendTemplateMsg(self, send_data):
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s'\
              % (self.getAccessToken())
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(send_data), headers=headers)
        data = response.json()
        return data

    def getTemplate(self):
        url = 'https://api.weixin.qq.com/cgi-bin/template/get_all_private_template?access_token=%s' \
              % (self.getAccessToken())
        resp = requests.get(url)
        data = resp.json()
        return data
