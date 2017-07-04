# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-04 17:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polyverif', '0006_auto_20170704_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='consensus_num',
            field=models.PositiveSmallIntegerField(default=3),
        ),
        migrations.AlterField(
            model_name='content',
            name='consensus',
            field=models.CharField(choices=[('D', 'Dispute'), ('C', 'Correct'), ('W', 'Wrong')], max_length=1, null=True),
        ),
    ]