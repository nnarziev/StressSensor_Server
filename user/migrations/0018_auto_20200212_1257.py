# Generated by Django 2.2.10 on 2020-02-12 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0017_auto_20200131_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='heartbeat_smartphone',
            field=models.BigIntegerField(default=1581479823.897469),
        ),
        migrations.AlterField(
            model_name='participant',
            name='last_ds_smartphone',
            field=models.BigIntegerField(default=1581479823.897469),
        ),
        migrations.AlterField(
            model_name='participant',
            name='last_login_datetime',
            field=models.BigIntegerField(default=1581479823.897469),
        ),
        migrations.AlterField(
            model_name='participant',
            name='register_datetime',
            field=models.BigIntegerField(default=1581479823.897469),
        ),
    ]
