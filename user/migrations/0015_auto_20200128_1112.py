# Generated by Django 2.2.4 on 2020-01-28 02:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_auto_20200128_1105'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apppackagetocategorymap',
            name='category',
            field=models.CharField(default='UNKNOWN', max_length=128),
        ),
        migrations.AlterField(
            model_name='participant',
            name='heartbeat_smartphone',
            field=models.BigIntegerField(default=1580177555.33077),
        ),
        migrations.AlterField(
            model_name='participant',
            name='last_ds_smartphone',
            field=models.BigIntegerField(default=1580177555.33077),
        ),
        migrations.AlterField(
            model_name='participant',
            name='last_login_datetime',
            field=models.BigIntegerField(default=1580177555.33077),
        ),
        migrations.AlterField(
            model_name='participant',
            name='register_datetime',
            field=models.BigIntegerField(default=1580177555.33077),
        ),
    ]
