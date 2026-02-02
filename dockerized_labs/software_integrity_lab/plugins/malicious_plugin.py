def run(request):
    return {
        "plugin_type": "modified",
        "integrity_verified": False,
        "status": "COMPROMISED",
        "leaked_user": "admin",
        "is_superuser": True,
        "message": "Plugin behavior altered after replacement"
    }
