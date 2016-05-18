# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jerry'

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import requests
import json
import time

from django.http import HttpResponse
import hashlib
from WXBizMsgCrypt import WXBizMsgCrypt

# global value
token = 'bhsdfhsdfsdfhbnsdfjkhnsdfjkjhn'
component_appid="wxjhdfjfhfjdsfdklfsdjdf"
component_appsecret="hdfsjsdhsdfjkjfklsdjdfkljsdfsdfj"
encodingAESKey = "HNDJKSDFHKhndjkhkljsdflkKNDFHJKHSKLnfjkhsdfjkl"


class WxOpenCallback:
    def __init__(self):
        self.token = token

    def check_signature(self, pams):
        if not self.token:
            return HttpResponse('TOKEN is not defined!')

        signature = pams.get('signature', '')
        timestamp = pams.get('timestamp', '')
        nonce = pams.get('nonce', '')
        tmparr = [self.token, timestamp, nonce]
        tmparr.sort()
        string = ''.join(tmparr)
        string = hashlib.sha1(string).hexdigest()
        # print signature
        # print string
        return signature == string


class WxOpenSDK:
    def __init__(self, ticket):
        self.component_appid = component_appid
        self.component_appsecret = component_appsecret
        self.ticket = ticket

    def get_com_access_token(self):
        # load file
        json_file = open('com_access_token.json')
        data = json.load(json_file)
        json_file.close()

        component_access_token = data['component_access_token']

        now = time.time()
        if data['expire_time'] < now:
            url = "https://api.weixin.qq.com/cgi-bin/component/api_component_token"
            payload = {'component_appid': self.component_appid,
                   'component_appsecret': self.component_appsecret,
                   'component_verify_ticket': self.ticket}
            headers = {'content-type': 'application/json'}
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            component_access_token = json.loads(response.text)['component_access_token']
            data['component_access_token'] = component_access_token
            data['expire_time'] = int(now) + 7000
            # save file
            json_file = open('com_access_token.json', 'w')
            json_file.write(json.dumps(data))
            json_file.close()

        return component_access_token

    def get_pre_auth_code(self):
        # load file
        json_file = open('pre_auth_code.json')
        data = json.load(json_file)
        json_file.close()

        pre_auth_code = data['pre_auth_code']
        now = time.time()
        if data['expire_time'] < now:
            url = "https://api.weixin.qq.com/cgi-bin/component/api_create_preauthcode?component_access_token=%s"\
                  % self.get_com_access_token()
            payload = {'component_appid': self.component_appid}
            headers = {'content-type': 'application/json'}
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            pre_auth_code = json.loads(response.text)['pre_auth_code']
            data['pre_auth_code'] = pre_auth_code
            data['expire_time'] = int(now) + 1100
            # save file
            json_file = open('pre_auth_code.json', 'w')
            json_file.write(json.dumps(data))
            json_file.close()

        return pre_auth_code

    def get_authorization_info(self, authorization_code):
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_query_auth?component_access_token=%s' \
              % self.get_com_access_token()
        payload = {
            "component_appid": self.component_appid,
            "authorization_code": authorization_code
        }
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        data = response.json()
        return data['authorization_info']

    def get_refresh_authorizer_access_token(self, authorizer_appid, authorizer_refresh_token):
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_authorizer_token?component_access_token=%s' \
              % self.get_com_access_token()
        payload = {
            "component_appid": self.component_appid,
            "authorizer_appid": authorizer_appid,
            "authorizer_refresh_token": authorizer_refresh_token
        }
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        return response.json()

    def get_authorizer_info(self, authorizer_appid):
        url = 'https://api.weixin.qq.com/cgi-bin/component/api_get_authorizer_info?component_access_token=%s' \
              % self.get_com_access_token()
        payload = {
            "component_appid": self.component_appid,
            "authorizer_appid": authorizer_appid
        }
        headers = {'content-type': 'application/json'}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        data = response.json()
        return data['authorizer_info']


class WxUtils:
    def get_encrypt_xml(self, reply_xml, nonce):
        reply_xml=reply_xml.encode('utf-8')
        encrypt = WXBizMsgCrypt(token, encodingAESKey, component_appid)
        ret_encrypt, encrypt_xml = encrypt.EncryptMsg(reply_xml, nonce)
        if ret_encrypt == 0:
            return encrypt_xml
        else:
            return str(ret_encrypt)+' error'

    def get_decrypt_xml(self, encrypt_xml, msg_signature, timestamp, nonce):
        decrypt = WXBizMsgCrypt(token, encodingAESKey, component_appid)
        ret_decrypt, decrypt_xml = decrypt.DecryptMsg(encrypt_xml,
                                             msg_signature,
                                             timestamp,
                                             nonce)
        if ret_decrypt == 0:
            return decrypt_xml
        else:
            return str(ret_decrypt)+' error'
