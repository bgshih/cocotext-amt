from django.contrib import admin

from polyverif.models import *


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_contents', 'content_progress', 'num_sentinel_contents', 'num_unassigned_contents', 'num_tasks', 'num_completed_tasks')
admin.site.register(Project, ProjectAdmin)


class ProjectWorkerAdmin(admin.ModelAdmin):
    list_display = ('id', 'mturk_worker', 'project', 'num_responses', 'consensus_ratio', 'num_sentinel_responded', 'num_sentinel_correct', 'sentinel_accuracy')
    readonly_fields = list_display
admin.site.register(ProjectWorker, ProjectWorkerAdmin)


class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'hit', 'completed', 'num_submissions_required', 'num_contents', 'num_submissions')
    readonly_fields = list_display
admin.site.register(Task, TaskAdmin)


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'project_worker')
    readonly_fields = ('id', 'task', 'project_worker', 'answer')
admin.site.register(Submission, SubmissionAdmin)


class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'text_instance', 'status', 'sentinel', 'num_responses_required', 'num_responses', 'gt_verification', 'consensus')
    readonly_fields = list_display
    list_filter = ('status', 'sentinel')
admin.site.register(Content, ContentAdmin)


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'submission', 'content', 'project_worker', 'verification', 'sentinel_correct')
    readonly_fields = list_display
    list_filter = ('project_worker',)
admin.site.register(Response, ResponseAdmin)
