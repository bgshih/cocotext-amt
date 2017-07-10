from datetime import timedelta
from tqdm import tqdm
import uuid

from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_delete
from django.dispatch import receiver

from common.models import *
from common.utils import get_mturk_client, parse_answer_xml, polygon_iou


class Project(ModelBase):
    """Object that keeps track of the tasks and contents."""
    name = models.CharField(max_length=128, unique=True)

    # # Tasks are created by cycling the COCO-Text images
    # image_id_list = JSONField()
    # image_id_list_idx = models.PositiveIntegerField()

    def num_tasks(self):
        return self.tasks.count()

    def num_contents(self):
        return self.contents.count()

    # number of completed tasks
    def num_completed_tasks(self):
        return self.tasks.filter(completed=True).count()

    def sync(self):
        pass

    def __str__(self):
        return self.name


class ProjectWorker(ModelBase):
    """Extends MturkWorker."""
    mturk_worker = models.OneToOneField(
        MturkWorker,
        related_name='polyannot_worker'
    )

    project = models.ForeignKey(
        Project,
        related_name='project_workers'
    )

    def __str__(self):
        return self.id

    class Meta:
        unique_together = ('mturk_worker', 'project')


class Task(ModelBase):
    """ Extends MturkHIT """
    hit = models.OneToOneField(
        MturkHit,
        related_name='polyannot_task'
    )

    completed = models.BooleanField(default=False)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    image = models.ForeignKey(
        CocoTextImage,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    def __str__(self):
        return str(self.id)


class Submission(ModelBase):
    """Extends MturkAssignment with relationships to task, worker, etc."""

    assignment = models.OneToOneField(
        MturkAssignment,
        related_name='polyannot_submission'
    )

    task = models.ForeignKey(
        Task,
        related_name='submissions'
    )

    project_worker = models.ForeignKey(
        ProjectWorker,
        related_name='submissions'
    )

    answer = JSONField()

    def create_contents(self):
        """Create contents from answer."""
        pass

    def __str__(self):
        return str(self.id)

    class Meta:
        # a worker should not produce more than one submissions per task
        unique_together = ('task', 'project_worker')


class Content(ModelBase):
    """Task data."""

    TYPE_CHOICES = (
        ('ST', 'Static'),  # statically displayed content
        ('HI', 'Hint'),    # V1 contents verified as wrong or disputed are used as hints
        ('SE', 'Sentinel') # displayed as hints, but has known answers
    )

    project       = models.ForeignKey(Project, related_name='contents')
    text_instance = models.OneToOneField(CocoTextInstance,
                                         on_delete=models.CASCADE,
                                         related_name='polyannot_content')
    type          = models.CharField(max_length=2, choices=TYPE_CHOICES)
    tasks         = models.ManyToManyField(Task, related_name='contents')

    def __str__(self):
        return str(self.id)


class Response(ModelBase):
    """Worker annotations."""
    task       = models.ForeignKey(Task, related_name='responses')
    submission = models.ForeignKey(Submission, related_name='responses')
    worker     = models.ForeignKey(ProjectWorker, related_name='responses')

    # Respond to which content.
    # The field is only used in hinted annotation mode
    # In free annotation mode, the field is None
    content = models.ForeignKey(Content, null=True)

    # Polygon drawn by worker.
    # If worker mark the hint as invalid, this field is None.
    polygon = JSONField(null=True)

    # Each response creates a new text_instance if polygon is not None.
    text_instance = models.OneToOneField(
        CocoTextInstance,
        related_name='polyannot_response',
        null=True
    )

    def sentinel_correct(self, iou_threshold=0.7):
        """If responding to a sentienl content, judge whether the answer is correct."""
        if self.content is None or self.content.type == 'SE':
            # not responding to a content or the content is not sentinel
            return None

        sentinel_polygon = self.content.text_instance.polygon
        iou = polygon_iou(self.polygon, sentinel_polygon)
        return iou >= iou_threshold

    def save(self, create_instance=True, *args, **kwargs):
        if self.text_instance is None and self.polygon is not None:
            # create a new text_instance
            if self.content is None:
                parent_instance = None
            else:
                parent_instance = self.content.text_instance

            self.text_instance = CocoTextInstance.create(
                id              = str(uuid.uuid4()),
                image           = task.image,
                polygon         = polygon,
                from_v1         = False,
                parent_instance = parent_instance
            )

        super(Response, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)