from django.contrib import admin
from django.utils.html import format_html

# Register your models here.
from api.models import *


admin.site.register(Experiment)


class CocoTextImageAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in CocoTextImage._meta.fields]
    list_display = [f.name for f in CocoTextImage._meta.fields if not \
        f.name in ('added', 'updated')
    ]
admin.site.register(CocoTextImage, CocoTextImageAdmin)


class CocoTextInstanceAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in CocoTextInstance._meta.fields]
    list_display = [f.name for f in CocoTextInstance._meta.fields if not \
        f.name in ('added', 'updated', 'polygon')
    ]
admin.site.register(CocoTextInstance, CocoTextInstanceAdmin)


class TextInstanceForPolygonVerificationAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in TextInstanceForPolygonVerification._meta.fields]
    list_display = [f.name for f in TextInstanceForPolygonVerification._meta.fields if not \
        f.name in ('added', 'updated')
    ]
admin.site.register(TextInstanceForPolygonVerification, TextInstanceForPolygonVerificationAdmin)


class PolygonVerificationTaskAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in PolygonVerificationTask._meta.fields]
    list_display = [f.name for f in PolygonVerificationTask._meta.fields if not \
        f.name in ('added', 'updated')
    ]
admin.site.register(PolygonVerificationTask, PolygonVerificationTaskAdmin)


class MturkHitAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in MturkHit._meta.fields]
    list_display = [
        f.name for f in MturkHit._meta.fields if not \
            f.name in ('hit_type_id', 'hit_group_id')
    ]
admin.site.register(MturkHit, MturkHitAdmin)


class MturkAssignmentAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in MturkAssignment._meta.fields]
    list_display = [ f.name for f in MturkAssignment._meta.fields if not \
        f.name in ('added', 'updated', 'answer')
    ]
    list_display.append('duration')
admin.site.register(MturkAssignment, MturkAssignmentAdmin)


class MturkWorkerAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in MturkWorker._meta.fields]
    list_display = [ f.name for f in MturkWorker._meta.fields if not \
        f.name in ('added', 'updated')
    ]
admin.site.register(MturkWorker, MturkWorkerAdmin)
