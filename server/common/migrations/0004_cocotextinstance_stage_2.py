# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-23 08:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_cocotextimage_misc_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='cocotextinstance',
            name='stage_2',
            field=models.BooleanField(default=False),
        ),
    ]
