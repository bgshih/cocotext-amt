from django.db import models
from django.conf import settings

import boto3

from api.utils import get_mturk_client


class MtWorker(models.Model):
    """
    MTurk worker
    NOTE: Do not create this class directly.
    """
    #: use Amazon's id
    id = models.CharField(max_length=128, primary_key=True)


class MtkHit(models.Model):
    """ MTurk HIT (Human Intelligence Task, corresponds to a MTurk HIT object) """

    # TODO
    #: use Amazon's id
    id = models.CharField(max_length=128, primary_key=True)
    hit_type = models.ForeignKey(MtHitType, related_name='hits')

    lifetime_in_seconds = models.IntegerField(null=True, blank=True)
    # expired = models.BooleanField(default=False)
    sandbox = models.BooleanField(default=(lambda: settings.MTURK_SANDBOX))

    #: if True, at least one assignment has been submitted (useful for filtering)
    any_assignments_submitted = models.BooleanField(default=False)
    #: if True, all assignments have been submitted (useful for filtering)
    all_assignments_submitted = models.BooleanField(default=False)

    # assignment data -- only updated after a sync
    max_assignments = models.IntegerField(default=1)
    num_assignments_pending = models.IntegerField(null=True, blank=True)
    num_assignments_available = models.IntegerField(null=True, blank=True)
    num_assignments_completed = models.IntegerField(null=True, blank=True)

    # HIT contents
    title = models.CharField(max_length=256)
    keywords = models.CharField(max_length=256)
    description = models.CharField(max_length=4096)
    question = models.CharField(max_length=10*1024*1024)

    HIT_STATUSES = (
        ('A', 'Assignable'),
        ('U', 'Unassignable'),
        ('R', 'Reviewable'),
        ('E', 'Reviewing'),
        ('D', 'Disposed'),
    )
    str_to_hit_status = dict((v, k) for (k, v) in HIT_STATUSES)
    hit_status_to_str = dict((k, v) for (k, v) in HIT_STATUSES)
    hit_status = models.CharField(
        max_length=1, choices=HIT_STATUSES, null=True, blank=True)

    REVIEW_STATUSES = (
        ('N', 'NotReviewed'),
        ('M', 'MarkedForReview'),
        ('A', 'ReviewedAppropriate'),
        ('I', 'ReviewedInappropriate')
    )
    str_to_review_status = dict((v, k) for (k, v) in REVIEW_STATUSES)
    review_status_to_str = dict((k, v) for (k, v) in REVIEW_STATUSES)
    review_status = models.CharField(
        max_length=1, choices=REVIEW_STATUSES, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.sandbox = settings.MTURK_SANDBOX
            self.hit_status = 'A'

            # TODO: some fields are missing and some redundant
            # send request to AMT
            response = get_mturk_client().create_hit(
                MaxAssignments=self.max_assignments,
                AutoApprovalDelayInSeconds=self.auto_approval_delay_in_seconds,
                LifetimeInSeconds=self.lifetime_in_seconds,
                AssignmentDurationInSeconds=self.assignment_duration_in_seconds,
                Reward=self.reward,
                Title=self.title,
                Keywords=self.keywords,
                Description=self.description,
                Question=self.question,
                # RequesterAnnotation is not used
                # QualificationRequirements TODO
                # UniqueRequestToken is not used
                # AssignmentReviewPolicy is not used
                # HITReviewPolicy is not used
                # HITLayoutId is not used
                # HITLayoutParameters is not used
            )
            )['HIT']

            self.id = response['HITId']
            self.hit_type_id = response['HITTypeId']
            self.hit_group_id = response['HITGroupId']
            self.hit_layout_id = response['HITLayoutId']
            self.creation_time = response['CreationTime']
            self.expiration = response['Expiration']
            self.hit_status = str_to_hit_status(response['HITStatus'])
            self.review_status = str_to_review_status(response['HITReviewStatus'])
            self.num_assignments_pending = response['NumberOfAssignmentsPending']
            self.num_assignments_available = response['NumberOfAssignmentsAvailable']
            self.num_assignments_completed = response['NumberOfAssignmentsCompleted']

            super(MtHit, self).save(*args, **kwargs)

    def sync_status(self, sync_assignments=True):
        """ Sync statuses with AMT server """
        client = get_mturk_client()
        response = client.get_hit(HITId=self.id)['HIT']
        self.hit_status = response['HITStatus']
        self.review_status = response['HITReviewStatus']
        self.num_assignments_pending = response['NumberOfAssignmentsPending']
        self.num_assignments_available = response['NumberOfAssignmentsAvailable']
        self.num_assignments_completed = response['NumberOfAssignmentsCompleted']

        if sync_assignments:
            raise NotImplementedError('')

    def dispose(self, data=None):
        """ Dispose this HIT -- finalize all approve/reject decisions """
        raise NotImplementedError('')

    def __str__(self):
        return self.id
    
    class Meta:
        verbose_name = 'HIT'
        verbose_name_plural = 'HITs'


class MtAssignment(models.Model):
    """
    An assignment is a worker assigned to a HIT
    NOTE: Do not create this -- instead call sync_status() on a MtHit object
    """

    #: use the Amazon-provided ID as our ID
    id = models.CharField(max_length=128, primary_key=True)

    hit = models.ForeignKey(MtHit, related_name='assignments')
    worker = models.ForeignKey(MtWorker, null=True, blank=True)

    # sentinel test
    