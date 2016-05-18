# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'jerry'
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import json
import time
import logging
import datetime
import requests
import threading
from urllib import urlencode
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from lxml import etree
from wxopenserver import WxOpenSDK, WxOpenCallback, WxUtils
from .models import Authorization_info
from wxorder.models import TemplateMsg, Orderinfo

# Create your views here.


logger = logging.getLogger(__name__)

class WxThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        logger.info(get_time()+'WxThread HttpResponse("")')
        return HttpResponse('')

# 授权事件接收URL http://wx.domain.com/auth
@csrf_exempt
def auth(request):
    if request.method == 'GET':
        auth_code = request.GET.get('auth_code', '')
        expires_in = request.GET.get('expires_in', '')
        if len(auth_code) > 10 and int(expires_in) > 60:
            return HttpResponseRedirect('/wxorder/')
        json_file = open('com_ticket.json')
        data = json.load(json_file)
        json_file.close()
        if data['ComponentVerifyTicket'] == '':
            return HttpResponse('no ComponentVerifyTicket')
        ComponentVerifyTicket = data['ComponentVerifyTicket']
        wxOpenSDK = WxOpenSDK(ticket=ComponentVerifyTicket)
        pre_auth_code = wxOpenSDK.get_pre_auth_code()
        redirect_uri = "http://%s/auth" % request.get_host()
        url = "https://mp.weixin.qq.com/cgi-bin/componentloginpage?"
        params = {"component_appid": wxOpenSDK.component_appid,
                  "pre_auth_code": pre_auth_code,
                 "redirect_uri": redirect_uri}
        url = url + urlencode(params)
        return HttpResponseRedirect(url)
    else:
        wxOpenCallBack = WxOpenCallback()
        is_valid = wxOpenCallBack.check_signature(request.GET)
        # logger.info(get_time()+'get the post data valid is %s' % str(is_valid))
        if is_valid:
            # get the url params
            msg_signature = request.GET.get('msg_signature', '')
            timestamp = request.GET.get('timestamp', '')
            nonce = request.GET.get('nonce', '')
            # logger.info('success get msg_signature: %s, timestamp: %s, nonce: %s' % (msg_signature, timestamp, nonce))
            # get the xml
            encrypt_xml = smart_str(request.body)
            if encrypt_xml.find('ToUserName') == -1:
                encrypt_xml=encrypt_xml.replace('AppId', 'ToUserName')
            # logger.info('get the encrypt_xml: %s' % encrypt_xml)
            wxu = WxUtils()
            decryp_xml = wxu.get_decrypt_xml(encrypt_xml=encrypt_xml,
                                             msg_signature=msg_signature,
                                             timestamp=timestamp,
                                             nonce=nonce)
            # logger.info('get the decrypt_xml: %s' % decryp_xml)
            if decryp_xml.find(' error') == -1:
                ticket_xml = etree.fromstring(decryp_xml)
                infoType = ticket_xml.find('InfoType').text
                if infoType == 'component_verify_ticket':
                    data = {'ComponentVerifyTicket': ticket_xml.find('ComponentVerifyTicket').text}
                    json_file = open('com_ticket.json', 'w')
                    json_file.write(json.dumps(data))
                    json_file.close()
                elif infoType == 'unauthorized':
                    authorizerAppid = ticket_xml.find('AuthorizerAppid').text
                    authorization_info = get_object_or_404(Authorization_info, authorizer_appid=authorizerAppid)
                    authorization_info.is_authorized = False
                    authorization_info.save()
                elif infoType == 'authorized':
                    # load file
                    json_file = open('com_ticket.json')
                    data = json.load(json_file)
                    json_file.close()

                    if data['ComponentVerifyTicket'] == '':
                        return HttpResponse('')

                    ComponentVerifyTicket = data['ComponentVerifyTicket']
                    wxOpenSDK = WxOpenSDK(ticket=ComponentVerifyTicket)

                    authorizerAppid = ticket_xml.find('AuthorizerAppid').text
                    authorizationCode = ticket_xml.find('AuthorizationCode').text
                    codeExpiredTime = ticket_xml.find('AuthorizationCodeExpiredTime').text
                    now = time.time()
                    now = int(now)+7000
                    info = wxOpenSDK.get_authorization_info(authorization_code=authorizationCode)
                    auth_info = Authorization_info.objects.get(authorizer_appid=authorizerAppid)
                    if auth_info is None:
                        auth_info = Authorization_info(is_authorized=True,
                                                       authorizer_appid=authorizerAppid,
                                                       authorizer_access_token=info['authorizer_access_token'],
                                                       token_expires_time=now,
                                                       authorizer_refresh_token=info['authorizer_refresh_token'],
                                                       authorization_code=authorizationCode,
                                                       code_expires_time=codeExpiredTime)
                    else:
                        auth_info.is_authorized = True
                        auth_info.authorizer_access_token = info['authorizer_access_token']
                        auth_info.token_expires_time = now
                        auth_info.authorizer_refresh_token = info['authorizer_refresh_token']
                        auth_info.authorization_code = authorizationCode
                        auth_info.code_expires_time = codeExpiredTime
                    auth_info.save()
                elif infoType == 'updateauthorized':
                    authorizerAppid = ticket_xml.find('AuthorizerAppid').text
                    authorizationCode = ticket_xml.find('AuthorizationCode').text
                    codeExpiredTime = ticket_xml.find('AuthorizationCodeExpiredTime').text
                    authorization_info = get_object_or_404(Authorization_info, authorizer_appid=authorizerAppid)
                    authorization_info.authorization_code=authorizationCode
                    authorization_info.code_expires_time=codeExpiredTime
                    authorization_info.save()
        return HttpResponse("success")


def get_time():
    return datetime.datetime.strftime(datetime.datetime.now(),
                                      '%Y-%m-%d %H:%M:%S ')


# 公众号消息与事件接收URL http://wx.domain.com/receive/$APPID$
@csrf_exempt
def receive(request, wxid):
    if wxid.find('wx') != 0:
        return HttpResponse('')
    logger.info(get_time()+"request wxappid is %s" % wxid)
    if request.method == 'POST':
        wxOpenCallBack = WxOpenCallback()
        is_valid = wxOpenCallBack.check_signature(request.GET)
        if is_valid:
            # get the url params
            msg_signature = request.GET.get('msg_signature', '')
            timestamp = request.GET.get('timestamp', '')
            nonce = request.GET.get('nonce', '')

            # get the xml
            encrypt_xml = smart_str(request.body)
            # logger.info(get_time() + 'receive the request body encode: %s' % encrypt_xml)
            wxu = WxUtils()
            decrypt_xml = wxu.get_decrypt_xml(encrypt_xml=encrypt_xml,
                                              msg_signature=msg_signature,
                                              timestamp=timestamp,
                                              nonce=nonce)
            # logger.info(get_time() + 'decode: %s' % decrypt_xml)
            if decrypt_xml.find(' error') == -1:
                if wxid == 'wx570bc396a51b8ff8':
                    return weixin_check(decrypt_xml, nonce)
                xml = etree.fromstring(decrypt_xml)
                ToUserName = xml.find('ToUserName').text
                FromUserName = xml.find('FromUserName').text
                CreateTime = xml.find('CreateTime').text
                MsgType = xml.find('MsgType').text
                if MsgType == "text":
                    Content = xml.find('Content').text
                    # logger.info('got the content %s' % Content)
                    Content = 'hello ' + Content
                    return send_text_cont(fromu=FromUserName, tou=ToUserName, cont=Content, nonce=nonce)
                elif MsgType == "event":
                    event = xml.find("Event").text
                    logger.info('got the MsgType %s' % MsgType)
                    # 发送模板消息反馈
                    if event == "TEMPLATESENDJOBFINISH":
                        logger.info('got the event %s' % event)
                        status = xml.find("Status").text
                        msg_time = datetime.fromtimestamp(int(CreateTime))
                        tmsg = TemplateMsg(toUserName=ToUserName,
                                           fromUserName=FromUserName,
                                           createTime=msg_time,
                                           msgType=MsgType,
                                           event=event,
                                           status=status)
                        tmsg.save()
                    elif event == 'SCAN':
                        # logger.info('got the event %s' % event)
                        scene_id = xml.find("EventKey").text
                        # logger.info('got the scene_id %s' % scene_id)
                        o = get_object_or_404(Orderinfo, pk=int(scene_id))
                        eval_url = "http://%s/wxorder/%d/evalo?" % (request.get_host(), o.id)
                        params = {'uid': FromUserName}
                        eval_url = eval_url + urlencode(params)
                        eval_cont = '请您对技术人员%s进行评价，<a href="%s">前往评价</a>' \
                                  % (o.tech_user.u_name, eval_url)
                        return send_text_cont(fromu=FromUserName, tou=ToUserName, cont=eval_cont, nonce=nonce)
                    elif event == 'subscribe':
                        # logger.info('got the event %s' % event)
                        qrscene = xml.find("EventKey").text
                        if qrscene != '':
                            scene_id = qrscene.split('_')[-1]
                            # logger.info('got the scene_id %s' % scene_id)
                            o = get_object_or_404(Orderinfo, pk=int(scene_id))
                            eval_url = "http://%s/wxorder/%d/evalo?" % (request.get_host(), o.id)
                            params = {'uid': FromUserName}
                            eval_url = eval_url + urlencode(params)
                            eval_cont = '请您对技术人员%s进行评价，<a href="%s">前往评价</a>' \
                                      % (o.tech_user.u_name, eval_url)
                            return send_text_cont(fromu=FromUserName, tou=ToUserName, cont=eval_cont, nonce=nonce)
                    else:
                        return HttpResponse('')


def weixin_check(decrypt_xml, nonce):
    xml = etree.fromstring(decrypt_xml)
    ToUserName = xml.find('ToUserName').text
    FromUserName = xml.find('FromUserName').text
    MsgType = xml.find('MsgType').text
    if MsgType == 'event':
        event = xml.find("Event").text
        eval_cont = event+'from_callback'
        return send_text_cont(fromu=FromUserName, tou=ToUserName, cont=eval_cont, nonce=nonce)
    elif MsgType == 'text':
        Content = xml.find('Content').text
        logger.info('got the content %s' % Content)
        if Content == 'TESTCOMPONENT_MSG_TYPE_TEXT':
            reply_cont = Content+'_callback'
            return send_text_cont(FromUserName, tou=ToUserName, cont=reply_cont, nonce=nonce)
        elif Content.startswith('QUERY_AUTH_CODE'):
            # send_bank_response()
	    bank_resp = WxThread(1, "WxThread")
	    bank_resp.start()
            query_auth_code = Content.split(':')[1]
            json_file = open('com_ticket.json')
            data = json.load(json_file)
            json_file.close()
            if data['ComponentVerifyTicket'] == '':
                return HttpResponse('no ComponentVerifyTicket')
            ComponentVerifyTicket = data['ComponentVerifyTicket']
            wxOpenSDK = WxOpenSDK(ticket=ComponentVerifyTicket)
            info = wxOpenSDK.get_authorization_info(authorization_code=query_auth_code)
            authorizer_access_token = info['authorizer_access_token']
            post_cont = query_auth_code + '_from_api'
            post_custom_text_msg(touser=FromUserName,
                                 content=post_cont,
                                 stoken=authorizer_access_token)


# send all text msg
def send_text_cont(fromu, tou, cont, nonce):
    wxu = WxUtils()
    reply_xml = """
    <xml>
    <ToUserName><![CDATA[%s]]></ToUserName>
    <FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%d</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[%s]]></Content>
    </xml>""" % (fromu, tou, int(time.time()), cont)
    encrypt_xml = wxu.get_encrypt_xml(reply_xml=reply_xml, nonce=nonce)
    return HttpResponse(encrypt_xml)


# send bank msg
def send_bank_response():
    return HttpResponse('')


# send custom text msg
def post_custom_text_msg(touser, content, stoken):
    url = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s' % stoken
    payload = {
        "touser": touser,
        "msgtype": "text",
        "text":
        {
             "content": content
        }
    }
    headers = {'content-type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    logger.info(get_time()+'post_custom_text_msg return: ' + response.text)



