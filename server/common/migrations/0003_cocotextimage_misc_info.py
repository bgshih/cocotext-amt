# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-21 05:45
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_auto_20170827_0412'),
    ]

    operations = [
        migrations.AddField(
            model_name='cocotextimage',
            name='misc_info',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]
