import random
from datetime import timedelta
from tqdm import tqdm

from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_delete
from django.dispatch import receiver

from common.models import *
from common.utils import get_mturk_client, parse_answer_xml


VERIFICATION_CHOICES = (
    ('U', 'Unverified'),
    ('C', 'Correct'),
    ('W', 'Wrong')
)

class Project(ModelBase):
    """ An object that keeps track of the tasks and contents """
    
    name = models.CharField(max_length=128, unique=True)

    # total number of contents in this project
    def num_contents(self):
        return self.contents.count()

    # portion of completed contents
    def content_progress(self):
        if self.contents.count() == 0:
            return None
        portion = self.contents.filter(status='C').count() / self.contents.count()
        portion_str = '%.2f%%' % (portion * 100)
        return portion_str
    
    # number of sentinel contents
    def num_sentinel_contents(self):
        return self.contents.filter(sentinel=True).count()
    
    # number of assigned contents, i.e. included in a task or served as sentinel
    def num_unassigned_contents(self):
        return self.contents.filter(status='U').count()

    # number of tasks in this project
    def num_tasks(self):
        return self.tasks.count()

    # number of completed tasks
    def num_completed_tasks(self):
        return self.tasks.filter(completed=True).count()

    # sync with MTurk server to retrieve submissions, then update workers, responses
    def sync(self, skip_completed_tasks=True):
        tasks = self.tasks.filter(completed=False) if skip_completed_tasks == True else \
                self.tasks.all()
        print('[1/2] Synching tasks, submissions, responses, and workers')
        print('Synching {} tasks'.format(tasks.count()))
        for task in tqdm(tasks):
            task.sync()

        print('[2/2] Synching contents')
        pending_contents = self.contents.filter(status='P')
        print('Syching {} contents'.format(pending_contents.count()))
        for content in tqdm(pending_contents):
            content.save()

    def __str__(self):
        return self.name


class ProjectWorker(ModelBase):
    """Extends MturkWorker."""
    mturk_worker = models.OneToOneField(
        MturkWorker,
        related_name='polyverif_worker'
    )

    project = models.ForeignKey(
        Project,
        related_name='project_workers'
    )

    def num_responses(self):
        return self.responses.count()

    # ratio of consensus among the completed contents responded by this worker
    def consensus_ratio(self):
        responded_contents = [res.content for res in self.responses.all()]
        completed_contents = [c for c in responded_contents if c.status == 'C']
        consensus_contents = [c for c in completed_contents if c.consensus is not None]
        num_completed = len(completed_contents)
        num_reach_consensus = len(consensus_contents)
        consensus_ratio = None if num_completed == 0 else num_reach_consensus / num_completed
        return consensus_ratio

    def num_sentinel_responded(self):
        count = 0
        for response in self.responses.all():
            if response.content.sentinel == True:
                count += 1
        return count

    def num_sentinel_correct(self):
        count = 0
        for response in self.responses.all():
            if response.content.sentinel == True and response.sentinel_correct():
                count += 1
        return count

    def sentinel_accuracy(self):
        num_responded = self.num_sentinel_responded()
        num_correct = self.num_sentinel_correct()
        accuracy = None if num_responded == 0 else num_correct / num_responded
        return accuracy


class Task(ModelBase):
    """ Extends MturkHIT """
    hit = models.OneToOneField(
        MturkHit,
        related_name='polyverif_task'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    # task is completed, set automatically
    completed = models.BooleanField(default=False)
    def _get_completed(self):
        return self.num_submissions() >= self.hit.max_assignments

    def num_submissions_required(self):
        return self.hit.max_assignments

    def num_contents(self):
        return self.contents.count()

    def num_submissions(self):
        return self.submissions.count()

    def sync_submissions(self, sync_responses=True):
        for a in self.hit.assignments.all():
            if not hasattr(a, 'submission') or a.submission is None:
                # get or create worker
                project_worker, _ = ProjectWorker.objects.get_or_create(
                    project=self.project,
                    mturk_worker=a.worker
                )

                # create submission
                submission, created = Submission.objects.get_or_created(
                    assignment=a,
                    task=self,
                    project_worker=project_worker
                )

                # create responses from submission data
                if created and sync_responses:
                    submission.sync_responses()

    def sync_contents(self):
        for c in self.contents.all():
            c.save()

    # sync with MTurk to update HITs, assignments, submissions, and responses
    def sync(self, sync_submissions=True, sync_responses=True, sync_contents=True):
        # sync HIT and its assignments
        self.hit.sync(sync_assignments=True)

        if sync_submissions:
            self.sync_submissions(sync_responses=sync_responses)

        # update child contents
        if sync_contents:
            self.sync_contents()

        # update itself
        self.save()

    def save(self, *args, **kwargs):
        # set or update self.completed
        self.completed = self._get_completed()

        # this will also create HIT
        super(Task, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # update the contents of this task after delete
        contents = self.contents.all()
        super(Task, self).delete(*args, **kwargs)
        for c in contents:
            c.save()

    def __str__(self):
        return str(self.id)


class Submission(ModelBase):
    """Extends MturkAssignment with relationships to task, worker, etc."""

    assignment = models.OneToOneField(
        MturkAssignment,
        related_name='polyverif_submission'
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

    def save(self, *args, **kwargs):
        assert(self.task.hit == self.assignment.hit)
        assert(self.project_worker.mturk_worker == self.assignment.worker)

        # answer_xml won't change, so this only need to be called once
        if self.answer is None:
            self.answer = parse_answer_xml(self.assignment.answer_xml)

        super(Submission, self).save(*args, **kwargs)

    def sync_responses(self):
        assert(self.answer is not None and isinstance(self.answer, list))

        # update responses from the parsed data
        for response in self.data:
            instance_id = response['instanceId']
            verification = response['verificationStatus']

            content = Content.objects.get(text_instance=instance_id)

            # response is only created once
            Response.objects.get_or_create(
                submission=self,
                content=content,
                worker=self.worker,
                verification=verification
            )

    def __str__(self):
        return str(self.id)

    class Meta:
        # a worker should not produce more than one submissions per task
        unique_together = ('task', 'project_worker')


class Content(ModelBase):
    """Content included in a task. Extends CocoTextInstance."""

    CONTENT_STATUS_CHOICES = (
        ('U', 'Unassigned'),      # not assigned to a task
        ('P', 'Pending'),         # being worked on
        ('C', 'Completed')        # enough responses received, completed
    )
    CONSENSUS_CHOICES = (
        ('D', 'Dispute'), # responses varies
        ('C', 'Correct'), # all responded correct
        ('W', 'Wrong')    # all responded wrong
    )

    text_instance = models.OneToOneField(
        CocoTextInstance,
        on_delete=models.CASCADE,
        related_name='polyverif_content'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='contents'
    )

    # number of same responses to reach consensus
    consensus_num = models.PositiveSmallIntegerField(default=2)

    status = models.CharField(
        max_length=1,
        choices=CONTENT_STATUS_CHOICES,
        default='U'
    )
    def _get_status(self):
        if self.id is None:
            # before saving for the first time
            return 'U'
        elif self.sentinel == True or self.consensus is not None:
            # if content is sentinel or has reached consensus, mark it as Completed
            return 'C'
        elif self.tasks.count() > 0:
            # the content has been assigned to any tasks and is being worked
            return 'P'
        else:
            # not assigned to any tasks
            return 'U'

    # in which tasks is the content provided
    tasks = models.ManyToManyField(Task, related_name='contents')

    # is the content a sentinel
    sentinel = models.BooleanField(default=False)
    
    consensus = models.CharField(
        max_length=1,
        null=True, # null if not no consensus reached
        choices=CONSENSUS_CHOICES
    )
    def _get_consensus(self):
        # if sentinel, use groundtruth
        if self.sentinel == True:
            return None

        # A content is marked as Dispute if responses varies,
        # Correct or Wrong if at least self.num_consensus responses agree
        # self.consensus has None value if no conclusion reached
        verifications = [res.verification for res in self.responses.all()]
        if len(verifications) == 0:
            return None
        elif len(verifications) < self.consensus_num:
            if not all([v == verifications[0] for v in verifications]):
                return 'D'
            else:
                return None
        else: # len(verifications) >= self.consensus_num:
            if all([v == 'C' for v in verifications]):
                return 'C'
            elif all([v == 'W' for v in verifications]):
                return 'W'
            else:
                return 'D'
        
        # get verifications to this content
        verifications = [res.verification for res in self.responses.all()]
        if len(verifications) < self.consensus_num:
            # not enough responses received
            return None
        else:
            num_correct = len([v == 'C' for v in verifications])
            num_wrong = len([v == 'W' for v in verifications])
            assert(num_correct < self.consensus_num or num_wrong < self.consensus_num)
            if num_correct >= self.consensus_num:
                return 'C'
            elif num_wrong >= self.consensus_num:
                return 'W'
            else:
                # in dispute, usually it's one correct and wrong response
                return 'D'


    # groundtruth verification. None if not a sentinel
    gt_verification = models.CharField(
        max_length=1,
        null=True,
        choices=VERIFICATION_CHOICES
    )

    # number of responses received
    num_responses = models.PositiveIntegerField(default=0)
    def _get_num_responses(self):
        return self.responses.count()

    def save(self, *args, **kwargs):
        self.num_responses = self._get_num_responses()
        self.consensus = self._get_consensus()
        self.status = self._get_status()

        super(Content, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class Response(ModelBase):
    """Worker's response to a content. """
    
    # where the response was submitted
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='responses'
    )

    # responded to which content
    content = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        related_name='responses'
    )

    # who responded
    project_worker = models.ForeignKey(
        ProjectWorker,
        on_delete=models.CASCADE,
        related_name='responses'
    )

    # response data: the verification
    verification = models.CharField(
        max_length=1,
        choices=VERIFICATION_CHOICES
    )

    # return the correctness if responding a sentinel content
    def sentinel_correct(self):
        if self.content.sentinel == False:
            return None
        return self.verification == self.content.gt_verification

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = ('submission', 'content', 'project_worker')
