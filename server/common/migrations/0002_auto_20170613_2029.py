# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-13 20:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Experiment',
            new_name='HitSettings',
        ),
        migrations.RenameField(
            model_name='mturkhit',
            old_name='experiment',
            new_name='hit_settings',
        ),
    ]
