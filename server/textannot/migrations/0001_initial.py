# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-22 10:54
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0003_cocotextimage_misc_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('groundtruth_text', models.CharField(max_length=1024, null=True)),
                ('sentinel', models.BooleanField(default=False)),
                ('consensus', models.CharField(max_length=1024, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=128, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProjectWorker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('num_sentinel_responded', models.IntegerField(default=0)),
                ('num_sentinel_correct', models.IntegerField(default=0)),
                ('mturk_worker', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='textannot_worker', to='common.MturkWorker')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_workers', to='textannot.Project')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('text', models.CharField(max_length=1024)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='textannot.Content')),
                ('project_worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='textannot.ProjectWorker')),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('answer', django.contrib.postgres.fields.jsonb.JSONField()),
                ('assignment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='textannot_submission', to='common.MturkAssignment')),
                ('project_worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='textannot.ProjectWorker')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('completed', models.BooleanField(default=False)),
                ('hit', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='textannot_task', to='common.MturkHit')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='textannot.Project')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='submission',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='textannot.Task'),
        ),
        migrations.AddField(
            model_name='response',
            name='submission',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='textannot.Submission'),
        ),
        migrations.AddField(
            model_name='content',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contents', to='textannot.Project'),
        ),
        migrations.AddField(
            model_name='content',
            name='tasks',
            field=models.ManyToManyField(related_name='contents', to='textannot.Task'),
        ),
        migrations.AddField(
            model_name='content',
            name='text_instance',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='textannot_content', to='common.CocoTextInstance'),
        ),
        migrations.AlterUniqueTogether(
            name='submission',
            unique_together=set([('task', 'project_worker')]),
        ),
        migrations.AlterUniqueTogether(
            name='response',
            unique_together=set([('submission', 'content', 'project_worker')]),
        ),
    ]
