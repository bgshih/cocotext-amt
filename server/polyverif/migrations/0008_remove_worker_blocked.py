# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-20 20:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polyverif', '0007_auto_20170620_0454'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='worker',
            name='blocked',
        ),
    ]
