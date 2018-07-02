# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-30 13:42
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0005_auto_20180426_1242'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageCorrection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('correction', django.contrib.postgres.fields.jsonb.JSONField()),
                ('ct_image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='corrections', to='common.CocoTextImage')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InstanceCorrection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('correction', django.contrib.postgres.fields.jsonb.JSONField()),
                ('ct_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='corrections', to='common.CocoTextInstance')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
