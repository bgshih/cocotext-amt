from django.contrib import admin

from textannot.models import *


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'num_tasks', 'num_completed_tasks')
admin.site.register(Project, ProjectAdmin)


class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'sentinel', 'groundtruth_text', 'consensus', 'text_instance')
admin.site.register(Content, ContentAdmin)


class ProjectWorkerAdmin(admin.ModelAdmin):
    list_display = ('id', 'mturk_worker', 'nickname', 'num_responses', 'num_sentinel_responded', 'num_sentinel_correct', 'sentinel_accuracy')
admin.site.register(ProjectWorker, ProjectWorkerAdmin)


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('submission', 'content', 'project_worker', 'text', 'sentinel_correct')
admin.site.register(Response, ResponseAdmin)
