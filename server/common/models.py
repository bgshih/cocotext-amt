import json
from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.timezone import now

from common.utils import get_mturk_client, parse_answer_xml, validate_list_of_integer

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
    image_id = models.CharField(max_length=MAX_ID_LENGTH, unique=True) # Use MSCOCO image ID
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
    instance_id = models.CharField(max_length=MAX_ID_LENGTH, unique=True)
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

class MturkHitType(ModelBase):
    hit_type_id         = models.CharField(max_length=MAX_ID_LENGTH, unique=True)
    auto_approval_delay = models.DurationField(default=timedelta(days=14))
    assignment_duration = models.DurationField(default=timedelta(hours=1))
    reward              = models.DecimalField(decimal_places=2, max_digits=4)
    title               = models.CharField(max_length=256)
    keywords            = models.CharField(max_length=256)
    description         = models.TextField()
    qrequirements       = JSONField(null=True)

    FIELD_PARAM_MAPPINGS = (
        ('hit_type_id', 'HITTypeId'),
        ('auto_approval_delay', 'AutoApprovalDelayInSeconds',
            lambda f: int(f.total_seconds()),
            lambda p: timedelta(seconds=p)),
        ('assignment_duration', 'AssignmentDurationInSeconds',
            lambda f: int(f.total_seconds()),
            lambda p: timedelta(seconds=p)),
        ('reward', 'Reward',
            lambda f: str(f),
            lambda p: Decimal(p)),
        ('title', 'Title'),
        ('keywords', 'Keywords'),
        ('description', 'Description'),
        ('qrequirements', 'QualificationRequirements')
        # # FK related names
        # ('qualification_requirements', 'QualificationRequirements',
        #     lambda f: [r.to_params() for r in f],
        #     None)
    )

    def save(self, *args, **kwargs):
        if not self.id:
            params = get_parameters_from_fields(self, self.FIELD_PARAM_MAPPINGS,
                ('auto_approval_delay', 'assignment_duration', 'reward', 'title',
                 'keywords', 'description', 'qualification_requirements')
            )
            response = get_mturk_client().create_hit_type(**params)
            print('HITType {} created on MTurk'.format(response['HITTypeId']))
            self.hit_type_id = response['HITTypeId']
        super(HitType, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.id)

    class Meta:
        abstract = True


class MturkWorker(ModelBase):
    # obtained from AMT
    worker_id = models.CharField(
        max_length=MAX_ID_LENGTH
        unique=True
    )

    # should be set by calling block() and unblock()
    blocked = models.BooleanField(default=False)

    block_reason = models.TextField()
    unblock_reason = models.TextField()

    FIELD_PARAM_MAPPINGS = (
        ('worker_id', 'WorkerId'),
        ('block_reason', 'Reason'),
        ('unblock_reason', 'Reason')
    )

    def block(self):
        raise NotImplementedError('Banning workers are not encouraged.')

        params = get_parameters_from_fields(
            self, self.FIELD_PARAM_MAPPINGS,
            ('worker_id', 'block_reason'),
            skipe_none=True
        )
        get_mturk_client().create_worker_block(**params)
        print('MTurk Worker {} has been blocked from all HITs'.format(self.worker_id))
        self.blocked = True
        self.save()

    def unblock(self):
        params = get_parameters_from_fields(
            self, self.FIELD_PARAM_MAPPINGS,
            ('worker_id', 'unblock_reason'),
            skipe_none=True
        )
        get_mturk_client().delete_worker_block(**params)
        print('MTurk Worker {} has been unblocked from all HITs'.format(self.id))
        self.blocked = False
        self.save()

    def __str__(self):
        return self.worker_id

    class Meta:
        abstract = True


class MturkHit(ModelBase):
    """MTurk HIT"""

    HIT_STATUS_CHOICES = (
        ('A', 'Assignable'),
        ('U', 'Unassignable'),
        ('R', 'Reviewable'),
        ('E', 'Reviewing'),
        ('D', 'Disposed')
    )
    hit_status_key_to_str = dict((k, v) for (k, v) in HIT_STATUS_CHOICES)
    hit_status_str_to_key = dict((v, k) for (k, v) in HIT_STATUS_CHOICES)

    REVIEW_STATUS_CHOICES = (
        ('N', 'NotReviewed'),
        ('M', 'MarkedForReview'),
        ('A', 'ReviewedAppropriate'),
        ('I', 'ReviewedInappropriate')
    )
    review_status_key_to_str = dict((k, v) for (k, v) in REVIEW_STATUS_CHOICES)
    review_status_str_to_key = dict((v, k) for (k, v) in REVIEW_STATUS_CHOICES)

    hit_id                    = models.CharField(max_length=MAX_ID_LENGTH, unique=True)
    hit_type_id               = models.CharField(max_length=MAX_ID_LENGTH)
    hit_layout_id             = models.CharField(max_length=MAX_ID_LENGTH, null=True)
    hit_layout_parameters     = JSONField(null=True)
    hit_group_id              = models.CharField(max_length=MAX_ID_LENGTH)
    creation_time             = models.DateTimeField()
    hit_status                = models.CharField(max_length=1,
                                                 choices=HIT_STATUS_CHOICES)
    max_assignments           = models.PositiveSmallIntegerField()
    lifetime                  = models.DurationField()
    question                  = models.TextField()
    expiration                = models.DateTimeField()
    requester_annotation      = models.TextField(null=True)
    unique_request_token      = models.CharField(max_length=MAX_ID_LENGTH, null=True)
    hit_review_status         = models.CharField(max_length=1,
                                                 choices=REVIEW_STATUS_CHOICES)
    num_assignments_pending   = models.PositiveSmallIntegerField()
    num_assignments_available = models.PositiveSmallIntegerField()
    num_assignments_completed = models.PositiveSmallIntegerField()
    assignment_review_policy  = JSONField(null=True)
    hit_review_policy         = JSONField(null=True)

    FIELD_PARAM_MAPPINGS = (
        ('hit_id', 'HITId'),
        ('hit_type_id', 'HITTypeId'),
        ('hit_layout_id', 'HITLayoutId'),
        ('hit_layout_parameters', 'HITLayoutParameters'),
        ('hit_group_id', 'HITGroupId'),
        ('creation_time', 'CreationTime'),
        ('hit_status', 'HITStatus',
            lambda f, D=hit_status_key_to_str: D[f],
            lambda p, D=hit_status_str_to_key: D[p]),
        ('max_assignments', 'MaxAssignments'),
        ('lifetime', 'LifetimeInSeconds',
            lambda f: int(f.total_seconds()),
            lambda p: timedelta(seconds=p)),
        ('question', 'Question'),
        ('expiration', 'Expiration'),
        ('requester_annotation', 'RequesterAnnotation'),
        ('unique_request_token', 'UniqueRequestToken'),
        ('hit_review_status', 'HITReviewStatus',
            lambda f, D=review_status_str_to_key: D[f],
            lambda p: D=review_status_key_to_str: D[p]),
        ('num_assignments_pending', 'NumberOfAssignmentsPending'),
        ('num_assignments_available', 'NumberOfAssignmentsAvailable'),
        ('num_assignments_completed', 'NumberOfAssignmentsCompleted'),
        ('assignment_review_policy', 'AssignmentReviewPolicy'),
        ('hit_review_policy', 'HITReviewPolicy')
    )

    def sync_assignments(self):
        response = get_mturk_client().list_assignments_for_hit(
            HITId=self.hit_id,
            MaxResults=100, # assignments should never exceed 100
            AssignmentStatuses=['Submitted', 'Approved', 'Rejected']
        )['Assignments']
        for assignment_response in response:
            MturkAssignment.create_or_update_from_response(assignment_response, save=True)

    def sync(self, sync_assignments=True):
        """Sync status with AMT, also sync its assignments """
        response = get_mturk_client().get_hit(HITId=self.hit_id)['HIT']
        set_fields_from_params(
            self, response, self.FIELD_PARAM_MAPPINGS,
            ('hit_status', 'hit_review_status', 'num_assignments_pending',
             'num_assignments_available', 'num_assignments_completed')
        )
        self.save()

        if sync_assignments:
            self.sync_assignments()

    def save(self, *args, **kwargs):
        if not self.id: # ID is None or empty string
            # create a new HIT
            params = get_parameters_from_fields(
                self, self.FIELD_PARAM_MAPPINGS,
                ('hit_type_id', 'max_assignments', 'lifetime', 'question',
                 'requester_annotation', 'unique_request_token', 'assignment_review_policy',
                 'hit_review_policy', 'hit_layout_id', 'hit_layout_parameters'),
                skip_none=True
            )
            response = get_mturk_client().create_hit_with_hit_type(**params)['HIT']
            print('HIT {} created on MTurk with HITType {}'.format(
                response['HITId'], response['HITTypeId']))

            set_fields_from_params(
                self, response, self.FIELD_PARAM_MAPPINGS,
                ('hit_id', 'hit_group_id', 'creation_time', 'expiration', 'hit_status',
                 'hit_review_status', 'num_assignments_pending', 'num_assignments_available',
                 'num_assignments_completed')
            )

        super(MturkHit, self).save(*args, **kwargs)

    def __str__(self):
        return self.id


class MturkAssignment(ModelBase):
    ASSIGNMENT_STATUS_CHOICES = (
        ('S', 'Submitted'),
        ('A', 'Approved'),
        ('R', 'Rejected')
    )
    assignment_status_key_to_str = dict((k,v) for (k,v) in ASSIGNMENT_STATUS_CHOICES)
    assignment_status_str_to_key = dict((v,k) for (k,v) in ASSIGNMENT_STATUS_CHOICES)
    
    assignment_id      = models.CharField(max_length=MAX_ID_LENGTH, unique=True)
    assignment_status  = models.CharField(max_length=1, choices=ASSIGNMENT_STATUS_CHOICES)
    worker_id          = models.CharField(max_length=MAX_ID_LENGTH)
    hit_id             = models.CharField(max_length=MAX_ID_LENGTH)
    auto_approval_time = models.DateTimeField(null=True)
    accept_time        = models.DateTimeField(null=True)
    submit_time        = models.DateTimeField(null=True)
    approval_time      = models.DateTimeField(null=True)
    rejection_time     = models.DateTimeField(null=True)
    deadline           = models.DateTimeField(null=True)
    answer             = models.TextField(null=True)
    requester_feedback = models.TextField()

    def duration(self):
        return self.submit_time - self.accept_time

    FIELD_PARAM_MAPPINGS = (
        ('assignment_id', 'AssignmentId'),
        ('assignment_status', 'AssignmentStatus',
            lambda f, D=assignment_status_key_to_str: D[f],
            lambda p, D=assignment_status_str_to_key: D[p]),
        ('worker_id', 'WorkerId'),
        ('hit_id', 'HITId'),
        ('auto_approval_time', 'AutoApprovalTime'),
        ('accept_time', 'AcceptTime'),
        ('submit_time', 'SubmitTime'),
        ('approval_time', 'ApprovalTime'),
        ('rejection_time', 'RejectionTime'),
        ('deadline', 'Deadline'),
        ('answer', 'Answer'),
        ('requester_feedback', 'RequesterFeedback')
    )

    def approve(self, feedback=None, override_rejection=False):
        params = {
            'AssignmentId': self.assignment_id,
            'OverrideRejection': override_rejection
        }
        if feedback is not None:
            params['RequesterFeedback'] = feedback
        get_mturk_client().approve_assignment(**params)
        print('Assignment {} is approved'.format(self.assignment_id))

    def reject(self, feedback=None):
        params = {
            'AssignmentId': self.assignment_id,
        }
        if feedback is not None:
            params['RequesterFeedback'] = feedback
        get_mturk_client().reject_assignment(**params)
        print('Assignment {} is rejected'.format(self.assignment_id))

    def save(self, *args, **kwargs):
        if self.assignment_id == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            print('AssignmentId is ASSIGNMENT_ID_NOT_AVAILABLE, pass.')
            return
        super(MturkAssignment, self).save(*args, **kwargs)

    @classmethod
    def create_or_update_from_response(cls, response):
        try:
            assignment = cls.objects.get(assignment_id=response['AssignmentId'])
        except cls.DoesNotExist:
            assignment = cls()

        set_fields_from_params(
            assignment, response, assignment.FIELD_PARAM_MAPPINGS,
            ('assignment_id', 'worker_id', 'hit_id', 'assignment_status',
            'auto_approval_time', 'accept_time', 'submit_time', 'approval_time',
            'rejection_time', 'deadline', 'answer', 'requester_feedback')
        )
        assignment.save()
        return assignment

    def __str__(self):
        return self.assignment_id


class QualificationType(ModelBase):
    QUALIFICATION_TYPE_STATUS_CHOICES = (
        ('A', 'Active'),
        ('I', 'Inactive'),
    )
    qtype_status_key_to_str = dict((k,v) for (k,v) in QUALIFICATION_TYPE_STATUS_CHOICES)
    qtype_status_str_to_key = dict((v,k) for (k,v) in QUALIFICATION_TYPE_STATUS_CHOICES)

    qtype_id           = models.CharField(max_length=MAX_ID_LENGTH, unique=True)
    creation_time      = models.DateTimeField()
    name               = models.CharField(max_length=64)
    keywords           = models.CharField(max_length=256)
    description        = models.TextField()
    qtype_status       = models.CharField(max_length=1, choices=QUALIFICATION_TYPE_STATUS_CHOICES, default='A')
    test               = models.TextField()
    test_duration      = models.DurationField()
    answer_key         = models.TextField(null=True)
    retry_delay        = models.DurationField()
    is_requestable     = models.BooleanField()
    auto_granted       = models.BooleanField()
    auto_granted_value = models.IntegerField(null=True)

    FIELD_PARAM_MAPPINGS = (
        ('qtype_id', 'QualificationTypeId'),
        ('creation_time', 'CreationTime'),
        ('name', 'Name'),
        ('keywords', 'Keywords'),
        ('description', 'Description'),
        ('qtype_status', 'QualificationTypeStatus',
            lambda f, D=qtype_status_key_to_str: D[f],
            lambda p, D=qtype_status_str_to_key: D[p]),
        ('test', 'Test'),
        ('test_duration', 'TestDurationInSeconds',
            lambda f: int(f.total_seconds()),
            lambda p: timedelta(seconds=p)),
        ('answer_key', 'AnswerKey'),
        ('retry_delay', 'RetryDelayInSeconds',
            lambda f: int(f.total_seconds()),
            lambda p: timedelta(seconds=p)),
        ('is_requestable', 'IsRequestable'),
        ('auto_granted', 'AutoGranted'),
        ('auto_granted_value', 'AutoGrantedValue')
    )

    def associate_to_worker(self, worker_id, value=None, send_notification=False):
        params = {
            'QualificationTypeId': self.qtype_id,
            'WorkerId': worker_id,
            'SendNotification': send_notification
        }
        if value is not None:
            params['IntegerValue'] = value
        get_mturk_client().associate_qualification_with_worker(**params)
        worker, _ = MturkWorker.objects.get_or_create(worker_id=worker_id)
        print('QualificationType {} associated to worker {} with value {}. Notification{} sent'.format(
            self.qtype_id, worker, value, "" if send_notification else " not"
        ))
    
    def disassociate_from_worker(self, worker_id, reason=None):
        client = client or get_mturk_client()
        params = {
            'QualificationTypeId': self.qtype_id,
            'WorkerId': worker_id
        }
        if reason is not None:
            params['Reason'] = reason
        client.disassociate_qualification_from_worker(**params)
        worker, _ = MturkWorker.objects.get_or_create(worker_id=worker_id)
        print('QualificationType {} disassociated from worker {}'.format(self.qtype_id, worker))

    def save(self, *args, **kwargs):
        if not self.qtype_id: # ID is None or empty string
            # create QualificationType on MTurk
            params = get_parameters_from_fields(
                self, FIELD_PARAM_MAPPINGS,
                ('name', 'keywords', 'description', 'qtype_status', 'retry_delay',
                'test', 'test_duration', 'auto_granted', 'answer_key', 'auto_granted_value'),
                skip_none=True
            )
            response = get_mturk_client().create_qualification_type(**params)['QualificationType']
            print('QualificationType {} created on MTurk'.format(response['QualificationTypeId']))
            set_fields_from_params(
                self, response, FIELD_PARAM_MAPPINGS,
                ('qtype_id', 'creation_time', 'qtype_status', 'is_requestable')
            )
        else:
            # update QualificationType on Mturk
            params = get_parameters_from_fields(
                self, FIELD_PARAM_MAPPINGS,
                ('qtype_id', 'description', 'qtype_status', 'test', 'answer_key',
                 'test_duration', 'retry_delay', 'auto_granted', 'auto_granted_value'),
                skip_none=True
            )
            get_mturk_client().update_qualification_type(**params)
            print('QualificationType {} updated on MTurk'.format(self.id))

        super(QualificationType, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        get_mturk_client().delete_qualification_type(
            QualificationTypeId=self.qtype_id
        )
        print('QualificationType {} deleted on MTurk'.format(self.qtype_id))
        super(QualificationType, self).delete(*args, **kwargs)

    def sync(self, sync_requests=True):
        """ Sync status and its requests """
        # sync QualificationType status with MTurk
        response = get_mturk_client().get_qualification_type(
            QualificationTypeId=self.qtype_id
        )
        set_fields_from_params(
            self, response, FIELD_PARAM_MAPPINGS,
            ('qtype_status', 'is_requestable'))
        self.save()

        if sync_requests == True:
            max_results = 64
            next_token = None
            num_results = None
            while num_results is None or num_results == max_results:
                params = {
                    'QualificationTypeId': self.qtype_id,
                    'MaxResults': max_results
                }
                if next_token is not None:
                    params['NextToken'] = next_token
                response = get_mturk_client().list_qualification_requests(**params)
                num_results = response['NumResults']
                next_token = response['NextToken']
                
                for request in response['QualificationRequests']:
                    MturkWorker.get_or_create(worker_id=request['WorkerId'])
                    assert(self.qtype_id == request['QualificationTypeId'])
                    QualificationRequest.get_or_create(
                        qrequest_id = request['QualificationRequestId'],
                        qtype_id    = self.qtype_id,
                        worker_id   = request['WorkerId'],
                        test        = request['Test'],
                        answer      = request['Answer'],
                        submit_time = request['SubmitTime']
                    )

    def __str__(self):
        return str(self.qtype_id)


class QualificationRequirement(ModelBase):
    """Qualification type and other settings that are passed as parameters when creating HITs."""
    hit_type = models.ForeignKey(MturkHitType, related_name='qualification_requirements')
    hit_type_id = models.CharField(max_length=MAX_ID_LENGTH)

    qualification_type = models.ForeignKey(QualificationType, on_delete=models.CASCADE)

    COMPARATOR_CHOICES = (
        ('LT', 'LessThan'),
        ('LE', 'LessThanOrEqualTo'),
        ('GT', 'GreaterThan'),
        ('GE', 'GreaterThanOrEqualTo'),
        ('EQ', 'EqualTo'),
        ('NE', 'NotEqualTo'),
        ('EX', 'Exists'),
        ('NX', 'DoesNotExist'),
        ('IN', 'In'),
        ('NI', 'NotIn')
    )
    comparator_key_to_str = {k:v for k, v in COMPARATOR_CHOICES}
    comparator = models.CharField(
        max_length=2,
        choices=COMPARATOR_CHOICES,
        null=True
    )

    # list of integers
    integer_values = JSONField()

    # list of locale values in dict {'Country': ..., 'Subdivision': ...}
    locale_values = JSONField()

    required_for_preview = models.BooleanField(default=False)

    def to_params(self):
        """Returns a dict of parameters for creating HIT"""
        requirement_params = {
            'QualificationTypeId': self.qualification_type.id,
            'Comparator': self.comparator_key_to_str[self.comparator],
            'IntegerValues': self.integer_values,
            'LocaleValues': self.locale_values,
            'RequiredToPreview': self.required_for_preview
        }
        return requirement_params


class QualificationRequest(ModelBase):
    """QualificationRequest should be created by calling QualificationType.sync """

    qrequest_id = models.CharField(max_length=MAX_ID_LENGTH, unique=True)
    qualification_type = models.ForeignKey(QualificationType, on_delete=models.CASCADE)

    # obtained from mturk
    worker      = models.ForeignKey(MturkWorker)
    test        = models.TextField()
    answer      = models.TextField()
    submit_time = models.DateTimeField()

    def accept(self, value=None):
        """ Accept request with an optional integer value attached to it. """
        params = {
            'QualificationRequestId': self.id
        }
        if value is not None:
            params['IntegerValue'] = value
        client.accept_qualification_request(**params)
        print('Qualification request {} by worker {} has been ACCEPTED on MTurk'.format(
            self.id, self.worker
        ))

    def reject(self, reason=None):
        """ Reject request. """
        reason = reason or 'Sorry, we cannot accept your request at this moment.'
        params = {
            'QualificationRequestId': self.id,
            'Reason': reason
        }
        client.reject_qualification_request(**params)
        print('Qualification request {} by worker {} has been REJECTED on MTurk'.format(
            self.id, self.worker
        ))

    def __str__(self):
        return self.id
