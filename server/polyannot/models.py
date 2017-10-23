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

    def sync(self, skip_completed_tasks=True):
        tasks = self.tasks.filter(completed=False) if skip_completed_tasks == True else \
                self.tasks.all()
        print('[1/2] Synching tasks, submissions, responses, and workers')
        print('Synching {} tasks'.format(tasks.count()))
        num_completed = 0
        for task in tqdm(tasks):
            task.sync()
            if task.completed:
                num_completed += 1
        print('{} tasks completed'.format(num_completed))


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

    admin = models.BooleanField(default=False)

    def num_submissions(self):
        return self.submissions.count()

    def average_duration(self):
        durations = [s.assignment.duration() for s in self.submissions.all()]
        avg_duration = sum(durations, timedelta(0)) / len(durations)
        return avg_duration

    def admin_accuracy(self, return_str=True):
        num_correct = self.submissions.filter(admin_mark='C').count()
        num_wrong = self.submissions.filter(admin_mark='W').count()
        num_total = (num_wrong + num_correct)
        if return_str:
            accuracy = 'N/A' if num_total == 0 else '{:.1f}% (among {})'.format(100 * num_correct / num_total, num_total)
        else:
            accuracy = 0.0 if num_total == 0 else num_correct / num_total
        return accuracy

    def __str__(self):
        return str(self.id)

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

    def sync_submissions(self, sync_responses=True, create_contents=True):
        for a in self.hit.assignments.all():
            # if hasattr(a, 'polyannot_submission') and a.polyannot_submission is not None:
            #     continue

            project_worker, _ = ProjectWorker.objects.get_or_create(
                project=self.project,
                mturk_worker=a.worker
            )

            submission, _ = Submission.objects.get_or_create(
                assignment=a,
                task=self,
                project_worker=project_worker
            )

            if sync_responses:
                submission.sync_responses(create_contents=create_contents)

    def sync(self, sync_submissions=True, sync_responses=True, create_contents=True):
        self.hit.sync(sync_assignments=True)
        if sync_submissions:
            self.sync_submissions(
                sync_responses=sync_responses,
                create_contents=create_contents
            )
        self.save()

    def save(self, *args, **kwargs):
        num_submissions_required = self.hit.max_assignments
        if self.submissions.count() >= num_submissions_required:
            self.completed = True
        super(Task, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class Submission(ModelBase):
    """Extends MturkAssignment with relationships to task, worker, etc."""

    ADMIN_MARK_TYPES = (
        ('U', 'Unchecked'),  # not checked yet
        ('C', 'Correct'),    # marked as correct
        ('W', 'Wrong'), # marked as wrong, should be rejected and reworked
        ('R', 'RevisionOrFurtherWork'), # needs revision or further work
    )

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

    answer = JSONField(null=True)

    admin_mark = models.CharField(
        max_length=1,
        choices=ADMIN_MARK_TYPES,
        default='U')

    # for miscellaneous use
    misc_info = JSONField(null=True)

    def sync_responses(self, create_contents=True):
        # the answer must be list of polygons, each represented by a list of points
        # each in {'x': ..., 'y': ...} format
        assert(self.answer is not None and isinstance(self.answer, dict))
        assert(create_contents == True)
        
        for i, polygon_data in enumerate(self.answer['polygons']):
            # if 'respondingContentId' in responseData:
            #     respondingContent = Content.objects.get(id=responseData['respondingContentId'])
            # else:
            #     respondingContent = None

            respondingContent = None

            Response.objects.get_or_create(
                task             = self.task,
                submission       = self,
                submission_idx   = i,
                project_worker   = self.project_worker,
                content          = respondingContent,
                polygon          = polygon_data,
            )

    def save(self, *args, **kwargs):
        if self.answer is None or not isinstance(self.answer, dict):
            answer = parse_answer_xml(self.assignment.answer_xml)
            if isinstance(answer, list):
                answer = {
                    'polygons': answer,
                    'hasRemainingText': None,
                }
            self.answer = answer

        super(Submission, self).save(*args, **kwargs)

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
    task           = models.ForeignKey(Task, related_name='responses')
    submission     = models.ForeignKey(Submission, related_name='responses')
    project_worker = models.ForeignKey(ProjectWorker, related_name='responses')
    # index within the submission
    submission_idx = models.PositiveSmallIntegerField()

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

    def create_instance(self):
        # create a new text_instance
        if self.content is None:
            parent_instance = None
        else:
            parent_instance = self.content.text_instance

        self.text_instance = CocoTextInstance.objects.create(
            id              = str(uuid.uuid4()),
            image           = self.task.image,
            polygon         = self.polygon,
            from_v1         = False,
            parent_instance = parent_instance
        )

    def save(self, create_instance=True, *args, **kwargs):
        if create_instance == True and self.text_instance is None and self.polygon is not None:
            # should only created once
            self.create_instance()

        super(Response, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = ('submission', 'submission_idx')
