# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-02 09:39
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corrections', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagecorrection',
            name='correction',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
    ]
