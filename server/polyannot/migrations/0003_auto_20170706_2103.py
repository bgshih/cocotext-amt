# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-06 21:03
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polyannot', '0002_task_completed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='image_id_list',
        ),
        migrations.RemoveField(
            model_name='project',
            name='image_id_list_idx',
        ),
    ]
