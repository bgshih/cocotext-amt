from django.contrib import admin

from polyverif.models import *


class PolygonVerificationTaskAdmin(admin.ModelAdmin):
    readonly_fields = [
        f.name for f in PolygonVerificationTask._meta.fields
    ]
    list_display = [
        f.name for f in PolygonVerificationTask._meta.fields if not \
            f.name in ('hit_type_id', 'hit_group_id', 'mturkhit_ptr')
    ]
    list_display.append('num_verification_instances')
admin.site.register(PolygonVerificationTask, PolygonVerificationTaskAdmin)


class PolygonVerificationInstanceAdmin(admin.ModelAdmin):
    readonly_fields = [
        f.name for f in PolygonVerificationInstance._meta.fields
    ]
    list_display = [
        f.name for f in PolygonVerificationInstance._meta.fields
    ]
admin.site.register(PolygonVerificationInstance, PolygonVerificationInstanceAdmin)

