# Generated by Django 2.2.4 on 2020-01-20 03:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.CharField(max_length=25, primary_key=True, serialize=False)),
                ('email', models.CharField(default='', max_length=25)),
                ('name', models.CharField(default='', max_length=25)),
                ('phone_num', models.CharField(default='', max_length=16)),
                ('device_info', models.TextField(blank=True, default='')),
                ('password', models.CharField(max_length=16)),
                ('register_datetime', models.BigIntegerField(default=1579489751.102259)),
                ('last_login_datetime', models.BigIntegerField(default=1579489751.102259)),
                ('heartbeat_smartwatch', models.BigIntegerField(default=1579489751.102259)),
                ('heartbeat_smartphone', models.BigIntegerField(default=1579489751.102259)),
                ('daily_data_size_smartwatch', models.FloatField(default=0)),
                ('daily_data_size_smartphone', models.FloatField(default=0)),
                ('last_ds_smartphone', models.BigIntegerField(default=1579489751.102259)),
                ('last_ds_smartwatch', models.BigIntegerField(default=1579489751.102259)),
                ('type', models.CharField(default='', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='ReceivedFilenames',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(max_length=22)),
                ('username', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='user.Participant')),
            ],
        ),
    ]
