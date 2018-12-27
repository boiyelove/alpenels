# Generated by Django 2.1.3 on 2018-12-27 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorial', '0004_auto_20181226_2031'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clientuser',
            name='last_login',
        ),
        migrations.RemoveField(
            model_name='clientuser',
            name='password',
        ),
        migrations.AddField(
            model_name='clientuser',
            name='email',
            field=models.EmailField(default='john@example.com', max_length=254, unique=True),
            preserve_default=False,
        ),
    ]