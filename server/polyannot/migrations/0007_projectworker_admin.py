# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-10 23:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polyannot', '0006_auto_20170710_2318'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectworker',
            name='admin',
            field=models.BooleanField(default=False),
        ),
    ]