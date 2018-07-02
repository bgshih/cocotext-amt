from django.db import models
from django.contrib.postgres.fields import JSONField

from common.models import ModelBase, CocoTextImage, CocoTextInstance


class ImageCorrection(ModelBase):
    ct_image = models.ForeignKey(CocoTextImage, related_name='corrections')
    correction = JSONField(null=True)

    def __str__(self):
        return str(self.id)

class InstanceCorrection(ModelBase):
    ct_instance = models.ForeignKey(CocoTextInstance, related_name='corrections')
    correction = JSONField()

    def __str__(self):
        return str(self.id)
