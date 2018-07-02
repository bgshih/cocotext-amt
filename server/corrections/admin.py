from django.contrib import admin

from corrections.models import ImageCorrection, InstanceCorrection


class InstanceCorrectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'ct_instance')
    readonly_fields = ('id', 'ct_instance')
admin.site.register(InstanceCorrection, InstanceCorrectionAdmin)

class ImageCorrectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'ct_image')
    readonly_fields = ('id', 'ct_image')
admin.site.register(ImageCorrection, ImageCorrectionAdmin)
