from django.contrib import admin

from common.models import *


class MturkHitTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'title', 'reward')
    readonly_fields = ('id', 'auto_approval_delay', 'assignment_duration', 'reward',
                       'title', 'keywords', 'description', 'qrequirements')
admin.site.register(MturkHitType, MturkHitTypeAdmin)


class CocoTextImageAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'filename', 'width', 'height', 'set', 'num_instances')
    list_display = readonly_fields
    list_filter = ('set',)
admin.site.register(CocoTextImage, CocoTextImageAdmin)


class CocoTextInstanceAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in CocoTextInstance._meta.fields]
    list_display = [f.name for f in CocoTextInstance._meta.fields if not \
        f.name in ('added', 'updated', 'polygon')
    ]
    list_filter = ('from_v1', 'stage_2')
admin.site.register(CocoTextInstance, CocoTextInstanceAdmin)


class MturkHitAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in MturkHit._meta.fields]
    list_display = [
        f.name for f in MturkHit._meta.fields if not \
            f.name in ('added', 'updated', 'question')
    ]
admin.site.register(MturkHit, MturkHitAdmin)


class MturkAssignmentAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in MturkAssignment._meta.fields]
    list_display = [ f.name for f in MturkAssignment._meta.fields if not \
        f.name in ('added', 'updated', 'answer_xml')
    ]
    list_display.append('duration')
admin.site.register(MturkAssignment, MturkAssignmentAdmin)


class MturkWorkerAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in MturkWorker._meta.fields]
    list_display = [ f.name for f in MturkWorker._meta.fields if not \
        f.name in ('added', 'updated')
    ]
admin.site.register(MturkWorker, MturkWorkerAdmin)


class QualificationTypeAdmin(admin.ModelAdmin):
    readonly_fields = ('added', 'updated', 'id', 'creation_time', 'is_requestable')
    list_display = ('id', 'slug', 'creation_time', 'name', 'is_requestable')
admin.site.register(QualificationType, QualificationTypeAdmin)


class QualificationRequestAdmin(admin.ModelAdmin):
    readonly_fields = ('added', 'updated', 'id', 'qtype', 'worker', 'test', 'answer', 'submit_time')
    list_display = ('id', 'qtype', 'worker', 'submit_time')
admin.site.register(QualificationRequest, QualificationRequestAdmin)
