# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-08-27 04:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qualificationtype',
            name='retry_delay',
            field=models.DurationField(null=True),
        ),
        migrations.AlterField(
            model_name='qualificationtype',
            name='test',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='qualificationtype',
            name='test_duration',
            field=models.DurationField(null=True),
        ),
    ]