from django.contrib import admin

from textannot.models import *


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'num_tasks', 'num_completed_tasks')
admin.site.register(Project, ProjectAdmin)
