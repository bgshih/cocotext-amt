from django.contrib import admin

from polyverif.models import *


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'hit_settings', 'num_contents', 'content_progress', 'num_sentinel_contents', 'num_unassigned_contents', 'num_tasks', 'num_completed_tasks')
admin.site.register(Project, ProjectAdmin)


class WorkerAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'mturk_worker', 'blocked', 'num_responses', 'consensus_ratio', 'num_sentinel_responded', 'num_sentinel_correct', 'sentinel_accuracy')
    readonly_fields = ('id', 'project', 'mturk_worker', 'blocked', 'num_responses', 'consensus_ratio', 'num_sentinel_responded', 'num_sentinel_correct', 'sentinel_accuracy')
admin.site.register(Worker, WorkerAdmin)

class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'hit', 'num_submissions_required', 'num_submissions', 'completed', 'num_contents')
    readonly_fields = ('id', 'project', 'hit', 'num_submissions', 'completed', 'num_contents')
admin.site.register(Task, TaskAdmin)


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment', 'task', 'worker')
    readonly_fields = ('id', 'assignment', 'task', 'worker', 'data')
admin.site.register(Submission, SubmissionAdmin)


class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'text_instance', 'status', 'sentinel', 'num_responses_required', 'num_responses', 'consensus')
    readonly_fields = ('project', 'text_instance', 'status', 'tasks', 'num_responses', 'consensus')
    list_filter = ('status', 'sentinel')
admin.site.register(Content, ContentAdmin)


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'submission', 'content', 'worker', 'verification', 'sentinel_correct')
    readonly_fields = list_display
    list_filter = ('worker',)
admin.site.register(Response, ResponseAdmin)
