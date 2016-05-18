#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


class Authorization_info(models.Model):
    """
    is_authorized, authorizer_appid,
    authorizer_access_token
    token_expires_time, authorizer_refresh_token,
    authorization_code, code_expires_time
    """
    is_authorized = models.BooleanField(verbose_name='is_authorized', default=True)
    authorizer_appid = models.CharField(max_length=30, verbose_name='公众号ID')
    authorizer_access_token = models.CharField(max_length=150, verbose_name='公众号token')
    token_expires_time = models.IntegerField(verbose_name='过期时间')
    authorizer_refresh_token = models.CharField(max_length=100, verbose_name='刷新token令牌')

    authorization_code = models.CharField(max_length=150, verbose_name='授权码', default=0)
    code_expires_time = models.IntegerField(verbose_name='授权码过期时间', default=0)