from django.contrib import admin

from polyannot.models import *


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'num_tasks', 'num_contents', 'num_completed_tasks')
admin.site.register(Project, ProjectAdmin)


class ProjectWorkerAdmin(admin.ModelAdmin):
    list_display = ('id', 'mturk_worker', 'project', 'admin', 'num_submissions', 'average_duration', 'admin_accuracy')
    readonly_fields = ('id', 'mturk_worker', 'project')
admin.site.register(ProjectWorker, ProjectWorkerAdmin)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'hit', 'completed', 'project', 'image')
    readonly_fields = list_display
    list_filter = ('completed',)
admin.site.register(Task, TaskAdmin)


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment', 'task', 'project_worker')
    readonly_fields = ('id', 'assignment', 'task', 'project_worker', 'answer')
admin.site.register(Submission, SubmissionAdmin)


class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'text_instance', 'type')
    readonly_fields = ('id', 'project', 'text_instance', 'type', 'tasks')
admin.site.register(Content, ContentAdmin)


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'submission', 'submission_idx', 'project_worker', 'content', 'text_instance')
    readonly_fields = ('id', 'task', 'submission', 'submission_idx', 'project_worker', 'content', 'text_instance', 'polygon')
admin.site.register(Response, ResponseAdmin)
