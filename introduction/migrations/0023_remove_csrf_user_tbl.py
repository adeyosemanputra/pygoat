from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("introduction", "0022_remove_owasp2017_lab_models"),
        ("introduction", "0022_remove_owasp2021_lab_models"),
    ]

    operations = [
        migrations.DeleteModel(name="CSRF_user_tbl"),
    ]
