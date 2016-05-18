from django.contrib import admin
from .models import Authorization_info

# Register your models here.

class Auth_infoAdmin(admin.ModelAdmin):
    """
    is_authorized, authorizer_appid,
    authorizer_access_token
    token_expires_time, authorizer_refresh_token,
    authorization_code, code_expires_time
    """
    fields = ['authorizer_appid', 'authorizer_access_token', 'authorizer_refresh_token']
    list_display = ('authorizer_appid', 'token_expires_time', 'code_expires_time', 'is_authorized')
    search_fields = ['authorizer_appid']

admin.site.register(Authorization_info, Auth_infoAdmin)
