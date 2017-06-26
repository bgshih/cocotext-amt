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
    
    # Project Settings
    # name of the project
    name = models.CharField(max_length=128)

    # hit settings
    hit_settings = models.ForeignKey(
        HitSettings,
        on_delete=models.PROTECT
    )

    # # qualification test data
    # qualification_test_contents = JSONField()
    # qualification_type = models.ForeignKey(QualificationType)
    
    def create_tasks(self, max_num_tasks=None):
        """ Create new tasks from pending and sentinel contents """

        # constants
        num_content_per_task = settings.POLYVERIF_NUM_CONTENT_PER_TASK
        sentinel_portion = settings.POLYVERIF_SENTINEL_PORTION

        unassigned_contents = self.contents.filter(status='U')
        sentinel_contents = self.contents.filter(sentinel=True)
        num_sentinel = sentinel_contents.count()

        if num_sentinel == 0:
            sentinel_portion = 0

        max_num_tasks_possible = int((unassigned_contents.count() / (1 - sentinel_portion)) / num_content_per_task)

        if max_num_tasks is None:
            # assign all unassigned
            num_tasks = max_num_tasks_possible
            num_to_assign = unassigned_contents.count()
        else:
            num_tasks = min(max_num_tasks_possible, max_num_tasks)
            num_to_assign = int(num_tasks * num_content_per_task * (1 - sentinel_portion))

        num_total_contents = num_tasks * num_content_per_task
        num_sentinel_to_assign = num_total_contents - num_to_assign

        print('Going to create %d tasks for %d unassigned contents and %d sentinel contents' % \
              (num_tasks, num_to_assign, num_sentinel_to_assign))
        if input('Continue? [y/n] ') != 'y':
            print('Aborted.')
            return

        # positive number means the index of content to assign
        # negative number means the (-index-1) of sentinel
        content_indices = [-(i % num_sentinel + 1) for i in range(num_sentinel_to_assign)] + \
                          list(range(num_to_assign))
        random.shuffle(content_indices)

        for i in tqdm(range(num_tasks)):
            task = Task(project=self)
            task.save(create_hit=True)
            for j in range(num_content_per_task):
                content_index = content_indices[i * num_content_per_task + j]
                if content_index < 0:
                    content = sentinel_contents[-content_index - 1]
                else:
                    content = unassigned_contents[content_index]
                content.tasks.add(task)
                content.save()

    # total number of contents in this project
    def num_contents(self):
        return self.contents.count()

    # portion of completed contents
    def content_progress(self):
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
    def sync(self, client=None, skip_completed_tasks=True):
        tasks = self.tasks.filter(completed=False) if skip_completed_tasks == True else \
                self.tasks.all()
        print('[1/2] Synching tasks, submissions, responses, and workers')
        print('Synching {} tasks'.format(tasks.count()))
        for task in tqdm(tasks):
            task.sync(client=client)

        print('[2/2] Synching contents')
        pending_contents = self.contents.filter(status='P')
        print('Syching {} contents'.format(pending_contents.count()))
        for content in tqdm(pending_contents):
            content.save()

    def __str__(self):
        return self.name


class Worker(ModelBase):
    """ Extends MturkWorker """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_workers'
    )

    mturk_worker = models.ForeignKey(
        MturkWorker,
        on_delete=models.CASCADE,
        related_name='project_workers'
    )

    def blocked(self):
        return self.mturk_worker.blocked

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

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = ('project', 'mturk_worker')


class Task(ModelBase):
    """ Extends MturkHIT """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )

    hit = models.OneToOneField(MturkHit, null=True, related_name='task')

    # default is project.hit_settings.max_assignments
    num_submissions_required = models.PositiveSmallIntegerField()

    # task is completed, set automatically
    completed = models.BooleanField(default=False)

    def num_contents(self):
        return self.contents.count()

    def num_submissions(self):
        return self.submissions.count()
    
    # sync with MTurk to update HITs, assignments, submissions, and responses
    def sync(self, client=None):
        # sync HIT and its assignments
        self.hit.sync(client=client, sync_assignments=True)

        # sync with HIT's assignments
        for a in self.hit.assignments.all():
            if not hasattr(a, 'submission') or a.submission is None:
                # create worker
                worker, _ = Worker.objects.get_or_create(project=self.project, mturk_worker=a.worker)

                # create a submission from assignment
                s, created = Submission.objects.get_or_create(assignment=a, task=self, worker=worker)

                # create responses from submission data
                if created:
                    s.create_responses()

        self.save()

        # update child contents
        for c in self.contents.filter(status='P'):
            c.save()


    def save(self, create_hit=True, *args, **kwargs):
        # set self.hit
        if self.hit is None and create_hit:
            self.hit = self.project.hit_settings.new_hit()

        # set self.num_submissions_required
        if self.num_submissions_required is None:
            self.num_submissions_required = self.project.hit_settings.max_assignments

        # set or update self.completed
        self.completed = (self.num_submissions() >= self.num_submissions_required)
        
        super(Task, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.hit.delete()
        # update the contents of this task after delete
        contents = self.contents.all()
        super(Task, self).delete(*args, **kwargs)
        for content in contents:
            content.save()

    def __str__(self):
        return str(self.id)


class Submission(ModelBase):
    """ Extends MturkAssignment """

    # the corresponding MTurk assignment
    assignment = models.OneToOneField(MturkAssignment, related_name='submission')

    # submit for which task, set by assignment.hit.task during save()
    task = models.ForeignKey(Task, related_name='submissions')

    # who submitted, set by assignment.worker during save()
    worker = models.ForeignKey(Worker, related_name='submissions')

    # JSON data, set by assignment.answer_xml during save()
    data = JSONField()

    def save(self, *args, **kwargs):
        # set task from HIT
        if self.task is None:
            self.task = self.assignment.hit.task

        # set worker from assignment
        if self.worker is None:
            self.worker, _ = Worker.objects.get_or_create(
                project=self.task.project,
                mturk_worker=self.assignment.worker
            )
        assert(self.worker.mturk_worker.id == self.assignment.worker.id)

        # set data by parsing assignment's answer_xml
        # assignment.answer_xml won't change, so this only need to be called once
        if self.data is None:
            self.data = parse_answer_xml(self.assignment.answer_xml)

        super(Submission, self).save(*args, **kwargs)

    def create_responses(self):
        assert(self.data is not None and isinstance(self.data, list))

        # update responses from the parsed data
        for response in self.data:
            instance_id = response['instanceId']
            verification = response['verificationStatus']

            content = Content.objects.get(text_instance=instance_id)

            # response is only created once
            response = Response.objects.get_or_create(
                submission=self,
                content=content,
                worker=self.worker,
                verification=verification
            )

    def __str__(self):
        return str(self.id)

    class Meta:
        # a worker should not produce more than one submissions per task
        unique_together = ('task', 'worker')


class Content(ModelBase):
    """ Content included in a task """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='contents'
    )

    # content data
    text_instance = models.ForeignKey(
        CocoTextInstance,
        on_delete=models.CASCADE
    )

    # content status
    CONTENT_STATUS_CHOICES = (
        ('U', 'Unassigned'),      # not assigned to a task
        ('P', 'Pending'),         # assigned to a task, not enough responses received
        ('C', 'Completed')        # enough responses received, completed
    )
    status = models.CharField(
        max_length=1,
        choices=CONTENT_STATUS_CHOICES
    )

    # num responses required, default is settings.POLYVERIF_MIN_CONSENSUS_COUNT
    num_responses_required = models.PositiveSmallIntegerField()

    # in which tasks is the content provided
    tasks = models.ManyToManyField(Task, related_name='contents')

    # is the content a sentinel
    sentinel = models.BooleanField(default=False)

    # groundtruth verification, non-null only if sentinel
    gt_verification = models.CharField(
        max_length=1,
        null=True,
        choices=VERIFICATION_CHOICES
    )

    # number of responses received
    def num_responses(self):
        return self.responses.count()

    # the consensus verification, None if no consensus is reached
    def get_consensus(self):
        # if sentinel, use groundtruth
        if self.sentinel == True:
            return self.gt_verification

        if self.status != 'C':
            return None

        consensus_min = settings.POLYVERIF_MIN_CONSENSUS_COUNT
        num_correct = 0
        num_wrong = 0
        for res in self.responses.all():
            if res.verification == 'C':
                num_correct += 1
            elif res.verification == 'W':
                num_wrong += 1

        if num_correct >= consensus_min:
            result = 'C'
        elif num_wrong >= consensus_min:
            result = 'W'
        else:
            result = None
        return result

    consensus = models.CharField(
        max_length=1,
        null=True,
        choices=VERIFICATION_CHOICES
    )

    def save(self, *args, **kwargs):
        # set value for num_responses_required
        if self.num_responses_required is None:
            self.num_responses_required = settings.POLYVERIF_MIN_CONSENSUS_COUNT

        # update status
        if self.responses.count() >= self.num_responses_required or self.sentinel:
            # content status is completed if 1) enough responses received, 2) is sentinel
            self.status = 'C'
        elif self.id is not None and self.tasks.count() > 0:
            # pending if assigned to some tasks
            self.status = 'P'
        else:
            self.status = 'U'

        # update consensus status
        self.consensus = self.get_consensus()

        super(Content, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class Response(ModelBase):
    """ Worker's response to a content. """
    
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
    worker = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    # response data: the verification
    verification = models.CharField(max_length=1, choices=VERIFICATION_CHOICES)

    # return the correctness if responding a sentinel content
    def sentinel_correct(self):
        if self.content.sentinel == False:
            return None
        return self.verification == self.content.gt_verification

    def __str__(self):
        return str(self.id)

    class Meta:
        unique_together = ('submission', 'content', 'worker')
