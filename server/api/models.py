from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder

MAX_ID_LENGTH = 1024
MAX_STATUS_LENGTH = 256
MAX_TEXT_LENGTH = 10485760 # 10MB


################################################
# MTurk Objects
################################################

class MturkHit(models.Model):
    hit_id                          = models.CharField(max_length=MAX_ID_LENGTH)
    hit_type_id                     = models.CharField(max_length=MAX_ID_LENGTH)
    hit_group_id                    = models.CharField(max_length=MAX_ID_LENGTH)
    creation_time                   = models.DateTimeField()
    hit_status                      = models.CharField(max_length=MAX_STATUS_LENGTH)
    max_assignments                 = models.PositiveSmallIntegerField()
    reward                          = models.DecimalField(max_digits=5, decimal_places=2)
    expiration                      = models.DateTimeField()
    hit_review_status               = models.CharField(max_length=MAX_STATUS_LENGTH)
    number_of_assignments_pending   = models.PositiveSmallIntegerField()
    number_of_assignments_available = models.PositiveSmallIntegerField()
    number_of_assignments_completed = models.PositiveSmallIntegerField()
    raw_data                        = JSONField(encoder=DjangoJSONEncoder)

    def __str__(self):
        return self.hit_id


class MturkAssignment(models.Model):
    accept_time        = models.DateTimeField()
    answer             = models.CharField(max_length=MAX_TEXT_LENGTH)
    auto_approval_time = models.DateTimeField()
    assignment_id      = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)
    assignment_status  = models.CharField(max_length=MAX_STATUS_LENGTH)
    hit_id             = models.CharField(max_length=MAX_ID_LENGTH)
    submit_time        = models.DateTimeField()
    worker_id          = models.CharField(max_length=MAX_ID_LENGTH)
    mturk_hit          = models.ForeignKey(MturkHit, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.assignment_id)


################################################
# HIT Task Data
################################################

class PolygonAnnotationTask(models.Model):
    coco_image_id  = models.CharField(max_length=MAX_ID_LENGTH)
    hints          = JSONField()
    v1_annot_ids   = JSONField()
    existing_annot = JSONField()
    mturk_hit      = models.OneToOneField(MturkHit,
                                          blank=True,
                                          null=True,
                                          on_delete=models.CASCADE,
                                          related_name='polygon_annotation_task')

    def num_hints(self):
        return len(self.hints)

    def __str__(self):
        return str(self.id)


class PolygonVerificationTask(models.Model):
    mturk_hit      = models.OneToOneField(MturkHit,
                                          blank=True,
                                          null=True,
                                          on_delete=models.CASCADE,
                                          related_name='polygon_verification_task')

    def __str__(self):
        return str(self.id)
