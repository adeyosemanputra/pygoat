from django.contrib import admin

from .models import (
    FAANG,
    CSRF_user_tbl,
    comments,
    info,
    login,
    otp,
    tickits,
)

# Register your models here.
admin.site.register(FAANG)
admin.site.register(info)
admin.site.register(login)
admin.site.register(comments)
admin.site.register(otp)
admin.site.register(tickits)
admin.site.register(CSRF_user_tbl)
