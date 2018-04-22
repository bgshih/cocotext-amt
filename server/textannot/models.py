import random
from datetime import timedelta
from tqdm import tqdm

from django.db import models
from django.contrib.postgres.fields import JSONField

from common.models import *
from common.utils import get_mturk_client, parse_answer_xml


class Project(ModelBase):
    name = models.CharField(max_length=128, unique=True)

    def num_tasks(self):
        return self.tasks.count()

    def num_completed_tasks(self):
        return self.tasks.filter(completed=True).count()

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

        print('[2/2] Updating worker statistics')

    def __str__(self):
        return self.name


class ProjectWorker(ModelBase):
    """Extends MturkWorker."""

    mturk_worker = models.OneToOneField(
        MturkWorker,
        related_name='textannot_worker'
    )
    project = models.ForeignKey(
        Project,
        related_name='project_workers'
    )

    def num_responses(self):
        return self.responses.count()

    num_sentinel_responded = models.IntegerField(default=0)
    num_sentinel_correct = models.IntegerField(default=0)
    def _calculate_sentinel_statistics(self):
        num_sentinel_responded = 0
        num_sentinel_correct = 0
        for response in self.responses.all():
            if response.content.sentinel == True:
                num_sentinel_responded += 1
                if response.sentinel_correct():
                    num_sentinel_correct += 1
        return num_sentinel_responded, num_sentinel_correct

    def sentinel_accuracy(self):
        accuracy = (None if self.num_sentinel_responded == 0 else
                    self.num_sentinel_correct / self.num_sentinel_responded)
        return accuracy


class Task(ModelBase):
    """ Extends MturkHIT """

    hit = models.OneToOneField(
        MturkHit,
        related_name='textannot_task'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    completed = models.BooleanField(default=False)
    def _get_completed(self):
        return self.num_submissions() >= self.hit.max_assignments

    def num_submissions_required(self):
        return self.hit.max_assignments

    def num_contents(self):
        return self.contents.count()

    def num_submissions(self):
        return self.submissions.count()

    def _sync_submissions(self, sync_responses=True):
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

    def _sync_contents(self):
        for c in self.contents.all():
            c.save()

    # sync with MTurk to update HITs, assignments, submissions, and responses
    def sync(self, sync_submissions=True, sync_responses=True, sync_contents=True):
        self.hit.sync(sync_assignments=True)
        if sync_submissions:
            self._sync_submissions(sync_responses=sync_responses)
        if sync_contents:
            self._sync_contents()
        self.save()

    def save(self, *args, **kwargs):
        self.completed = self._get_completed()
        super(Task, self).save(*args, **kwargs) # this will call self.hit.save() and create HIT

    def delete(self, *args, **kwargs):
        contents = self.contents.all()
        super(Task, self).delete(*args, **kwargs)
        # update the contents of this task after deletion
        for c in contents:
            c.save()

    def __str__(self):
        return str(self.id)


class Submission(ModelBase):
    """Extends MturkAssignment with relationships to task, worker, etc."""

    assignment = models.OneToOneField(
        MturkAssignment,
        related_name='textannot_submission'
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
            text = response['text']
            content = Content.objects.get(text_instance=instance_id)
            # response is only created once
            Response.objects.get_or_create(
                submission=self,
                content=content,
                project_worker=self.project_worker,
                text=text
            )

    def __str__(self):
        return str(self.id)

    class Meta:
        # a worker has at most one submission per task
        unique_together = ('task', 'project_worker')


class Content(ModelBase):
    """Content included in a task. Extends CocoTextInstance."""

    text_instance = models.OneToOneField(
        CocoTextInstance,
        on_delete=models.CASCADE,
        related_name='textannot_content'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='contents'
    )
    tasks = models.ManyToManyField(Task, related_name='contents')
    groundtruth_text = models.CharField(max_length=1024, null=True)
    sentinel = models.BooleanField(default=False)
    consensus = models.CharField(max_length=1024, null=True)

    def _get_consensus(self):
        if self.sentinel == True:
            return self.groundtruth_text
        elif self.responses.count() < 2:
            return None
        else:
            consensus = None
            text_count = {}
            for response in self.responses:
                if response.text not in text_count:
                    text_count[response.text] = 0
                text_count[response.text] += 1
            for text, text_count in text_count.items():
                if text_count >= 2:
                    consensus = text
                    break
            return consensus

    def save(self, *args, **kwargs):
        self.consensus = self._get_consensus()
        super(Content, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class Response(ModelBase):
    """Worker's response to a content. """
    
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    content = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    project_worker = models.ForeignKey(
        ProjectWorker,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    text = models.CharField(max_length=1024)

    # return the correctness if responding a sentinel content
    def sentinel_correct(self):
        if self.content.sentinel == False:
            return None
        return self.text == self.content.groundtruth_text

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = ('submission', 'content', 'project_worker')
