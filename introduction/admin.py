from django.contrib import admin

from .models import (
    AF_admin,
    AF_session_id,
    CF_user,
    CSRF_user_tbl,
)

# Register your models here.
admin.site.register(CF_user)
admin.site.register(AF_admin)
admin.site.register(AF_session_id)
admin.site.register(CSRF_user_tbl)
