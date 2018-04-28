from django.contrib import admin

from textannot.models import *


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'num_tasks', 'num_completed_tasks')
admin.site.register(Project, ProjectAdmin)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'hit', 'completed', 'num_submissions_required', 'num_contents', 'num_submissions')
    readonly_fields = ('hit', 'project')
admin.site.register(Task, TaskAdmin)

class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'num_responses', 'sentinel', 'groundtruth_text', 'consensus', 'text_instance')
    list_filter = ('status', 'sentinel')
    readonly_fields = ('text_instance', 'project')
admin.site.register(Content, ContentAdmin)


class ProjectWorkerAdmin(admin.ModelAdmin):
    list_display = ('id', 'mturk_worker', 'nickname', 'num_responses', 'num_sentinel_responded', 'num_sentinel_correct', 'sentinel_accuracy')
admin.site.register(ProjectWorker, ProjectWorkerAdmin)


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('submission', 'content', 'project_worker', 'text', 'sentinel_correct')
admin.site.register(Response, ResponseAdmin)
