# Generated by Django 2.2.4 on 2020-01-20 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_auto_20200120_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='heartbeat_smartphone',
            field=models.BigIntegerField(default=1579510444.092384),
        ),
        migrations.AlterField(
            model_name='participant',
            name='heartbeat_smartwatch',
            field=models.BigIntegerField(default=1579510444.092384),
        ),
        migrations.AlterField(
            model_name='participant',
            name='last_ds_smartphone',
            field=models.BigIntegerField(default=1579510444.092384),
        ),
        migrations.AlterField(
            model_name='participant',
            name='last_ds_smartwatch',
            field=models.BigIntegerField(default=1579510444.092384),
        ),
        migrations.AlterField(
            model_name='participant',
            name='last_login_datetime',
            field=models.BigIntegerField(default=1579510444.092384),
        ),
        migrations.AlterField(
            model_name='participant',
            name='register_datetime',
            field=models.BigIntegerField(default=1579510444.092384),
        ),
    ]
