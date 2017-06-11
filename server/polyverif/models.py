from datetime import timedelta

from django.db import models
from django.contrib.postgres.fields import JSONField

from common.models import Experiment, ModelBase, MturkHit, MturkAssignment, CocoTextInstance
from common.utils import get_mturk_client, parse_answer_xml


class PolygonVerificationTask(ModelBase):
    experiment = models.ForeignKey(Experiment, related_name='polyverif_tasks')
    hit = models.OneToOneField(MturkHit, null=True, related_name='polyverif_task')

    def num_verification_instances(self):
        return self.verification_instances.count()

    def submissions(self):
        return [a.submission for a in self.hit.assignments.all()]
    
    def save(self, create_hit=True):
        if self.hit is None and create_hit:
            self.hit = self.experiment.new_hit(save=True)
        super(PolygonVerificationTask, self).save()

    def sync(self, client=None):
        """ Sync its HIT, HIT's assignments, and its submissions """
        self.hit.sync(client=client)
        for a in self.hit.assignments.all():
            try:
                submission = a.submission
            except PolygonVerificationSubmission.DoesNotExist:
                submission = PolygonVerificationSubmission(assignment=a)
            submission.sync()
        self.save()


class PolygonVerificationSubmission(ModelBase):
    assignment = models.OneToOneField(MturkAssignment, related_name='submission')
    answer = JSONField()

    def sync(self):
        """ Sync with its assignment. """
        answer = parse_answer_xml(self.assignment.answer_xml)
        self.save()


class PolygonVerificationInstance(ModelBase):
    """ Candidate text instances for polygon verification. """
    text_instance = models.OneToOneField(
        CocoTextInstance,
        related_name='for_polygon_verification'
    )

    # the task this verification instance belongs to
    task = models.ForeignKey(
        PolygonVerificationTask,
        related_name='verification_instances',
        null=True
    )

    def submissions(self):
        """ Submissions that contains this instance """
        return self.task.submissions()

    # this instance has been verified and will be used as a sentinel
    sentinel = models.BooleanField(default=False)

    def retrieve_answers(self, approved_only=False):
        """ Retrieve a dictionary of {worker_id: answer} for this instance. """
        if approved_only == True:
            raise NotImplementedError('')

        answers = {}
        for assignment in self.verification_task.hit.assignments.all():
            worker_id = assignment.worker.id
            answer_json = parse_amt_answer(assignment.answer)
            for instance_answer in answer_json:
                if 'id' in instance_answer and instance_answer['id'] == self.text_instance.id:
                    answers[worker_id] = instance_answer['status']
        return answers
    
    def verification_status(self):
        return self.text_instance.polygon_verification
