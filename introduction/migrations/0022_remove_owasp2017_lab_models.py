from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("introduction", "0021_csrf_user_tbl"),
    ]

    operations = [
        migrations.DeleteModel(name="info"),
        migrations.DeleteModel(name="FAANG"),
        migrations.DeleteModel(name="login"),
        migrations.DeleteModel(name="comments"),
        migrations.DeleteModel(name="authLogin"),
        migrations.DeleteModel(name="otp"),
        migrations.DeleteModel(name="tickits"),
    ]
