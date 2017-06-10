# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-08 21:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_auto_20170608_2044'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cocotextinstance',
            name='language_verified',
        ),
        migrations.RemoveField(
            model_name='cocotextinstance',
            name='legibility_verified',
        ),
        migrations.RemoveField(
            model_name='cocotextinstance',
            name='polygon_verified',
        ),
        migrations.RemoveField(
            model_name='cocotextinstance',
            name='text_verified',
        ),
        migrations.RemoveField(
            model_name='textinstanceforpolygonverification',
            name='gt_verification_status',
        ),
        migrations.RemoveField(
            model_name='textinstanceforpolygonverification',
            name='verification_status',
        ),
        migrations.AddField(
            model_name='cocotextinstance',
            name='language_verification',
            field=models.CharField(choices=[('U', 'Unverified'), ('C', 'Correct'), ('W', 'Wrong')], default='U', max_length=1),
        ),
        migrations.AddField(
            model_name='cocotextinstance',
            name='legibility_verification',
            field=models.CharField(choices=[('U', 'Unverified'), ('C', 'Correct'), ('W', 'Wrong')], default='U', max_length=1),
        ),
        migrations.AddField(
            model_name='cocotextinstance',
            name='polygon_verification',
            field=models.CharField(choices=[('U', 'Unverified'), ('C', 'Correct'), ('W', 'Wrong')], default='U', max_length=1),
        ),
        migrations.AddField(
            model_name='cocotextinstance',
            name='text_verification',
            field=models.CharField(choices=[('U', 'Unverified'), ('C', 'Correct'), ('W', 'Wrong')], default='U', max_length=1),
        ),
        migrations.AlterField(
            model_name='textinstanceforpolygonverification',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='textinstanceforpolygonverification',
            name='text_instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='for_polygon_verification', to='api.CocoTextInstance'),
        ),
    ]
