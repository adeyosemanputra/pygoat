from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("introduction", "0021_csrf_user_tbl"),
    ]

    operations = [
        migrations.DeleteModel(name="Blogs"),
        migrations.DeleteModel(name="sql_lab_table"),
        migrations.DeleteModel(name="CF_user"),
        migrations.DeleteModel(name="AF_session_id"),
        migrations.DeleteModel(name="AF_admin"),
    ]
