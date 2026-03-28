from django.contrib import admin

from .models import (FAANG, AF_admin, AF_session_id, CF_user, CSRF_user_tbl,
                     comments, info, login, otp, tickits)

# Register your models here.
admin.site.register(FAANG)
admin.site.register(info)
admin.site.register(login)
admin.site.register(comments)
admin.site.register(otp)
admin.site.register(tickits)
admin.site.register(CF_user)
admin.site.register(AF_admin)
admin.site.register(AF_session_id)
admin.site.register(CSRF_user_tbl)