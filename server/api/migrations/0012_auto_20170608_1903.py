# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-08 19:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20170607_1610'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mturkassignment',
            old_name='assignment_id',
            new_name='id',
        ),
    ]
