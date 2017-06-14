import json
from datetime import timedelta

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.timezone import now

from common.utils import get_mturk_client, parse_answer_xml

MAX_ID_LENGTH = 128


class ModelBase(models.Model):
    added = models.DateTimeField(default=now)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


################################################################################
# COCO-Text Objects
################################################################################

class CocoTextImage(ModelBase):
    id = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True) # Use MSCOCO image ID
    filename = models.CharField(max_length=256)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()

    SUBSET_CHOICES = (
        ('TRN', 'Training'),
        ('VAL', 'Validation'),
        ('TST', 'Test')
    )
    set = models.CharField(max_length=3, choices=SUBSET_CHOICES)

    def __str__(self):
        return str(self.id)


class CocoTextInstance(ModelBase):
    # If imported from v1, use original ID
    id = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)
    image = models.ForeignKey(CocoTextImage, on_delete=models.CASCADE)
    # Polygon format: [{x: number, y: number}, ...]
    polygon = JSONField()
    text = models.CharField(max_length=256, null=True)

    LEGIBILITY_CHOICES = (
        ('L', 'Legible'),
        ('I', 'Illegible')
    )
    legibility = models.CharField(max_length=1, choices=LEGIBILITY_CHOICES)

    TEXT_CLASS_CHOICES = (
        ('M', 'MachinePrinted'),
        ('H', 'Handwritten'),
        ('O', 'Others')
    )
    text_class = models.CharField(max_length=1, choices=TEXT_CLASS_CHOICES, null=True)

    language = models.CharField(max_length=128, null=True)
    from_v1 = models.BooleanField(default=False) # Instance is inherited from V1

    # verification status
    VERIFICATION_STATUS_CHOICES = (
        ('U', 'Unverified'),
        ('C', 'Correct'),
        ('W', 'Wrong'),
    )
    polygon_verification = models.CharField(max_length=1, choices=VERIFICATION_STATUS_CHOICES, default='U')
    text_verification = models.CharField(max_length=1, choices=VERIFICATION_STATUS_CHOICES, default='U')
    legibility_verification = models.CharField(max_length=1, choices=VERIFICATION_STATUS_CHOICES, default='U')
    language_verification = models.CharField(max_length=1, choices=VERIFICATION_STATUS_CHOICES, default='U')

    def __str__(self):
        return str(self.id)


################################################################################
# MTurk Objects
################################################################################

class HitSettings(ModelBase):
    name = models.CharField(max_length=64)
    version = models.CharField(max_length=16, default='0.0.1')

    # HIT settings
    max_assignments     = models.PositiveSmallIntegerField(default=1)
    auto_approval_delay = models.DurationField(default=timedelta(days=14))
    lifetime            = models.DurationField(default=timedelta(days=30))
    assignment_duration = models.DurationField(default=timedelta(hours=1))
    reward              = models.DecimalField(decimal_places=2, max_digits=4)
    title               = models.CharField(max_length=256)
    keywords            = models.CharField(max_length=256)
    description         = models.TextField()
    question            = models.TextField()

    def new_hit(self, save=True):
        """ Create a new HIT with the HIT settings """
        hit = MturkHit()
        hit.hit_settings = self
        if save:
            hit.save()
        return hit

    def __str__(self):
        return self.name


class MturkWorker(ModelBase):
    # obtained from AMT
    id = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)

    @classmethod
    def get_or_create(cls, worker_id):
        try:
            worker = cls.objects.get(id=worker_id)
        except MturkWorker.DoesNotExist:
            worker = cls(id=worker_id)
            worker.save()
        return worker

    def __str__(self):
        return self.id


class MturkHit(ModelBase):
    # obtained from AMT after HIT creation
    id            = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)
    hit_type_id   = models.CharField(max_length=MAX_ID_LENGTH)
    hit_group_id  = models.CharField(max_length=MAX_ID_LENGTH)
    creation_time = models.DateTimeField()
    expiration    = models.DateTimeField()

    hit_settings = models.ForeignKey(HitSettings, related_name='hits')

    HIT_STATUS_CHOICES = (
        ('A', 'Assignable'),
        ('U', 'Unassignable'),
        ('R', 'Reviewable'),
        ('E', 'Reviewing'),
        ('D', 'Disposed'))
    str_to_hit_status = dict((v, k) for (k, v) in HIT_STATUS_CHOICES)
    hit_status_to_str = dict((k, v) for (k, v) in HIT_STATUS_CHOICES)
    hit_status = models.CharField(max_length=1,
                                  choices=HIT_STATUS_CHOICES)

    REVIEW_STATUS_CHOICES = (
        ('N', 'NotReviewed'),
        ('M', 'MarkedForReview'),
        ('A', 'ReviewedAppropriate'),
        ('I', 'ReviewedInappropriate'))
    str_to_review_status = dict((v, k) for (k, v) in REVIEW_STATUS_CHOICES)
    review_status_to_str = dict((k, v) for (k, v) in REVIEW_STATUS_CHOICES)
    hit_review_status = models.CharField(max_length=1,
                                         choices=REVIEW_STATUS_CHOICES)

    num_assignments_pending   = models.PositiveSmallIntegerField()
    num_assignments_available = models.PositiveSmallIntegerField()
    num_assignments_completed = models.PositiveSmallIntegerField()

    def sync(self, client=None, sync_assignments=True):
        """ Sync status with AMT, also sync its assignments """
        client = client or get_mturk_client()
        response = client.get_hit(HITId=self.id)['HIT']

        self.hit_status                = self.str_to_hit_status[response['HITStatus']]
        self.review_status             = self.str_to_review_status[response['HITReviewStatus']]
        self.num_assignments_pending   = response['NumberOfAssignmentsPending']
        self.num_assignments_available = response['NumberOfAssignmentsAvailable']
        self.num_assignments_completed = response['NumberOfAssignmentsCompleted']

        self.save()

        # update all assignments
        if sync_assignments:
            response = client.list_assignments_for_hit(
                HITId=self.id,
                MaxResults=100, # assignments should never exceed 100
                AssignmentStatuses=['Submitted', 'Approved', 'Rejected']
            )['Assignments']
            for assignment_response in response:
                MturkAssignment.create_or_update_from_response(assignment_response, save=True)

    def save(self, client=None, *args, **kwargs):
        if not self.id:
            client = client or get_mturk_client()

            # Create a new HIT on MTurk
            response = client.create_hit(
                MaxAssignments              = self.hit_settings.max_assignments,
                AutoApprovalDelayInSeconds  = int(self.hit_settings.auto_approval_delay.total_seconds()),
                LifetimeInSeconds           = int(self.hit_settings.lifetime.total_seconds()),
                AssignmentDurationInSeconds = int(self.hit_settings.assignment_duration.total_seconds()),
                Reward                      = str(self.hit_settings.reward),
                Title                       = self.hit_settings.title,
                Keywords                    = self.hit_settings.keywords,
                Description                 = self.hit_settings.description,
                Question                    = self.hit_settings.question
                # RequesterAnnotation is not used
                # QualificationRequirements TODO
                # UniqueRequestToken is not used
                # AssignmentReviewPolicy is not used
                # HITReviewPolicy is not used
                # HITLayoutId is not used
                # HITLayoutParameters is not used
            )['HIT']

            self.id                        = response['HITId']
            self.hit_type_id               = response['HITTypeId']
            self.hit_group_id              = response['HITGroupId']
            self.creation_time             = response['CreationTime']
            self.expiration                = response['Expiration']
            self.hit_status                = self.str_to_hit_status[response['HITStatus']]
            self.review_status             = self.str_to_review_status[response['HITReviewStatus']]
            self.num_assignments_pending   = response['NumberOfAssignmentsPending']
            self.num_assignments_available = response['NumberOfAssignmentsAvailable']
            self.num_assignments_completed = response['NumberOfAssignmentsCompleted']

            print('HIT {} created on AMT'.format(response['HITId']))

        super(MturkHit, self).save(*args, **kwargs)

    def __str__(self):
        return self.id


class MturkAssignment(ModelBase):
    id     = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)
    worker = models.ForeignKey(MturkWorker, related_name='assignments', null=True)
    hit    = models.ForeignKey(MturkHit, related_name='assignments')

    ASSIGNMENT_STATUS_CHOICES = (
        ('S', 'Submitted'),
        ('A', 'Approved'),
        ('R', 'Rejected'))
    status_string_to_key = { v:k for k,v in ASSIGNMENT_STATUS_CHOICES }
    assignment_status = models.CharField(max_length=1,
                                         choices=ASSIGNMENT_STATUS_CHOICES)
    
    auto_approval_time = models.DateTimeField(null=True)
    accept_time        = models.DateTimeField(null=True)
    submit_time        = models.DateTimeField(null=True)
    approval_time      = models.DateTimeField(null=True)
    rejection_time     = models.DateTimeField(null=True)
    deadline           = models.DateTimeField(null=True)
    answer_xml         = models.TextField(null=True)

    def duration(self):
        return self.submit_time - self.accept_time

    def save(self, *args, **kwargs):
        if self.id == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            print('AssignmentId is ASSIGNMENT_ID_NOT_AVAILABLE, not going to save this.')
            return
        super(MturkAssignment, self).save(*args, **kwargs)

    @classmethod
    def create_or_update_from_response(cls, response, save=True):
        try:
            assignment = cls.objects.get(id=response['AssignmentId'])
        except cls.DoesNotExist:
            assignment = cls()

        attr_key_pairs = (
            ('id', 'AssignmentId'),
            ('worker', 'WorkerId'),
            ('hit', 'HITId'),
            ('assignment_status', 'AssignmentStatus'),
            ('auto_approval_time', 'AutoApprovalTime'),
            ('accept_time', 'AcceptTime'),
            ('submit_time', 'SubmitTime'),
            ('approval_time', 'ApprovalTime'),
            ('rejection_time', 'RejectionTime'),
            ('deadline', 'Deadline'),
            ('answer_xml', 'Answer')
            # RequesterFeedback is ignored
        )
        for attr, key in attr_key_pairs:
            if not key in response:
                continue
            value = response[key]
            if key == 'WorkerId':
                value = MturkWorker.get_or_create(value)
            elif key == 'HITId':
                value = MturkHit.objects.get(id=value)
            elif key == 'AssignmentStatus':
                value = assignment.status_string_to_key[value]
            setattr(assignment, attr, value)
        
        if save:
            assignment.save()

        return assignment

    def __str__(self):
        return str(self.id)
