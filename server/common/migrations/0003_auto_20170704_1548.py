# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-04 15:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_auto_20170703_1833'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qualificationrequest',
            name='qtype',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='common.QualificationType'),
        ),
    ]