from django.contrib import admin

# Register your models here.
from .models import MturkHit, MturkAssignment, PolygonAnnotationTask


class MturkHitAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in MturkHit._meta.fields]
    list_display = ('hit_id',
                    'creation_time',
                    'hit_status',
                    'number_of_assignments_completed')

admin.site.register(MturkHit, MturkHitAdmin)


class MturkAssignmentAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in MturkAssignment._meta.fields]
    list_display = ('assignment_id',
                    'assignment_status',
                    'worker_id',
                    'submit_time')

admin.site.register(MturkAssignment, MturkAssignmentAdmin)


class PolygonAnnotationTaskAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in PolygonAnnotationTask._meta.fields]
    list_display = ('id',
                    'coco_image_id',
                    'num_hints',
                    'mturk_hit')

admin.site.register(PolygonAnnotationTask, PolygonAnnotationTaskAdmin)

