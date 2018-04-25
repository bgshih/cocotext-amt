import json
from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.timezone import now

from common.utils import get_mturk_client, parse_answer_xml, \
    get_params_from_fields, set_fields_from_params

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
    SUBSET_CHOICES = (
        ('TRN', 'Training'),
        ('VAL', 'Validation'),
        ('TST', 'Test')
    )

    id       = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True) # Use MSCOCO image ID
    filename = models.CharField(max_length=256)
    width    = models.PositiveIntegerField()
    height   = models.PositiveIntegerField()
    set      = models.CharField(max_length=3, choices=SUBSET_CHOICES)

    misc_info = JSONField(null=True)

    def num_instances(self):
        return self.text_instances.count()

    def __str__(self):
        return str(self.id)


class CocoTextInstance(ModelBase):
    LEGIBILITY_CHOICES = (
        ('L', 'Legible'),
        ('I', 'Illegible')
    )

    TEXT_CLASS_CHOICES = (
        ('M', 'MachinePrinted'),
        ('H', 'Handwritten'),
        ('O', 'Others')
    )

    VERIFICATION_STATUS_CHOICES = (
        ('U', 'Unverified'),
        ('C', 'Correct'),
        ('W', 'Wrong'),
    )

    # If imported from v1, use original ID
    id                      = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)
    image                   = models.ForeignKey(CocoTextImage,
                                                related_name='text_instances',
                                                on_delete=models.CASCADE)
    # Polygon format : [{x: number, y: number}, ...]
    polygon                 = JSONField()
    text                    = models.CharField(max_length=256, null=True)
    language                = models.CharField(max_length=128, null=True)
    legibility              = models.CharField(max_length=1, choices=LEGIBILITY_CHOICES, null=True)
    text_class              = models.CharField(max_length=1, choices=TEXT_CLASS_CHOICES, null=True)
    # Instance is inherited from V1
    from_v1                 = models.BooleanField(default=False)
    
    # verifications
    polygon_verification    = models.CharField(max_length=1, choices=VERIFICATION_STATUS_CHOICES, default='U')
    text_verification       = models.CharField(max_length=1, choices=VERIFICATION_STATUS_CHOICES, default='U')
    legibility_verification = models.CharField(max_length=1, choices=VERIFICATION_STATUS_CHOICES, default='U')
    language_verification   = models.CharField(max_length=1, choices=VERIFICATION_STATUS_CHOICES, default='U')

    # create a new instance to correct an old one
    parent_instance         = models.ForeignKey('CocoTextInstance', null=True, related_name='child_instances')

    # Stage 2 annotations (text annotation)
    # Notes:
    # 1) In stage 2, polygon_verification, text_verification, legibility_verification,
    # language_verification, and parent_instance are no longer used and are kept only
    # for compatibility considerations
    # 2) In stage 2, instance IDs follow this format: "<IMAGE_ID>-<INSTNACE_INDEX>".
    # For example, "142497-001" is the first text instance of image "142497"
    stage_2                 = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


################################################################################
# MTurk Objects
################################################################################

class MturkHitType(ModelBase):
    id                  = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)
    auto_approval_delay = models.DurationField(default=timedelta(days=14))
    assignment_duration = models.DurationField(default=timedelta(hours=1))
    reward              = models.DecimalField(decimal_places=2, max_digits=4)
    title               = models.CharField(max_length=256)
    keywords            = models.CharField(max_length=256)
    description         = models.TextField()
    qrequirements       = JSONField(null=True)

    slug = models.CharField(
        max_length=128,
        unique=True
    )

    FIELD_PARAM_MAPPINGS = (
        ('id', 'HITTypeId'),
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
    )

    def save(self, *args, **kwargs):
        if not self.id: # None or empty string
            params = get_params_from_fields(self, self.FIELD_PARAM_MAPPINGS,
                ('auto_approval_delay', 'assignment_duration', 'reward', 'title',
                 'keywords', 'description', 'qrequirements')
            )
            response = get_mturk_client().create_hit_type(**params)
            print('HITType {} created on MTurk'.format(response['HITTypeId']))
            self.id = response['HITTypeId']
        super(MturkHitType, self).save(*args, **kwargs)

    def __str__(self):
        return self.slug


class MturkWorker(ModelBase):
    # obtained from AMT
    id = models.CharField(
        max_length=MAX_ID_LENGTH,
        primary_key=True
    )

    # should be set by calling block() and unblock()
    blocked = models.BooleanField(default=False)

    block_reason = models.TextField()
    unblock_reason = models.TextField()

    FIELD_PARAM_MAPPINGS = (
        ('id', 'WorkerId'),
        ('block_reason', 'Reason'),
        ('unblock_reason', 'Reason')
    )

    def block(self):
        raise NotImplementedError('Banning workers are not encouraged.')

        params = get_params_from_fields(
            self, self.FIELD_PARAM_MAPPINGS,
            ('id', 'block_reason'),
            skipe_none=True
        )
        get_mturk_client().create_worker_block(**params)
        print('MTurk Worker {} has been blocked from all HITs'.format(self.id))
        self.blocked = True
        self.save()

    def unblock(self):
        params = get_params_from_fields(
            self, self.FIELD_PARAM_MAPPINGS,
            ('id', 'unblock_reason'),
            skipe_none=True
        )
        get_mturk_client().delete_worker_block(**params)
        print('MTurk Worker {} has been unblocked from all HITs'.format(self.id))
        self.blocked = False
        self.save()

    def __str__(self):
        return str(self.id)


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

    id                        = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)
    hit_type                  = models.ForeignKey(MturkHitType, related_name='hits')
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
        ('id', 'HITId'),
        ('hit_type', 'HITTypeId',
            lambda f: f.id,
            lambda p: MturkHitType.objects.get(id=p)),
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
            lambda f, D=review_status_key_to_str: D[f],
            lambda p, D=review_status_str_to_key: D[p]),
        ('num_assignments_pending', 'NumberOfAssignmentsPending'),
        ('num_assignments_available', 'NumberOfAssignmentsAvailable'),
        ('num_assignments_completed', 'NumberOfAssignmentsCompleted'),
        ('assignment_review_policy', 'AssignmentReviewPolicy'),
        ('hit_review_policy', 'HITReviewPolicy')
    )

    def sync_assignments(self):
        response = get_mturk_client().list_assignments_for_hit(
            HITId=self.id,
            MaxResults=100, # assignments should never exceed 100
            AssignmentStatuses=['Submitted', 'Approved', 'Rejected']
        )['Assignments']
        for assignment_response in response:
            MturkAssignment.create_or_update_from_response(assignment_response)

    def sync(self, sync_assignments=True):
        """Sync status with AMT, also sync its assignments """
        response = get_mturk_client().get_hit(HITId=self.id)['HIT']
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
            params = get_params_from_fields(
                self, self.FIELD_PARAM_MAPPINGS,
                ('hit_type', 'max_assignments', 'lifetime', 'question',
                 'requester_annotation', 'unique_request_token', 'assignment_review_policy',
                 'hit_review_policy', 'hit_layout_id', 'hit_layout_parameters'),
                skip_none=True
            )
            response = get_mturk_client().create_hit_with_hit_type(**params)['HIT']
            print('HIT {} created on MTurk with HITType {}'.format(
                response['HITId'], response['HITTypeId']))

            set_fields_from_params(
                self, response, self.FIELD_PARAM_MAPPINGS,
                ('id', 'hit_group_id', 'creation_time', 'expiration', 'hit_status',
                 'hit_review_status', 'num_assignments_pending', 'num_assignments_available',
                 'num_assignments_completed')
            )

        super(MturkHit, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class MturkAssignment(ModelBase):
    ASSIGNMENT_STATUS_CHOICES = (
        ('S', 'Submitted'),
        ('A', 'Approved'),
        ('R', 'Rejected')
    )
    assignment_status_key_to_str = dict((k,v) for (k,v) in ASSIGNMENT_STATUS_CHOICES)
    assignment_status_str_to_key = dict((v,k) for (k,v) in ASSIGNMENT_STATUS_CHOICES)
    
    id                 = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)
    assignment_status  = models.CharField(max_length=1, choices=ASSIGNMENT_STATUS_CHOICES)
    worker             = models.ForeignKey(MturkWorker, related_name='assignments')
    hit                = models.ForeignKey(MturkHit, related_name='assignments')
    auto_approval_time = models.DateTimeField(null=True)
    accept_time        = models.DateTimeField(null=True)
    submit_time        = models.DateTimeField(null=True)
    approval_time      = models.DateTimeField(null=True)
    rejection_time     = models.DateTimeField(null=True)
    deadline           = models.DateTimeField(null=True)
    answer_xml         = models.TextField(null=True)
    requester_feedback = models.TextField(null=True)

    def duration(self):
        return self.submit_time - self.accept_time

    FIELD_PARAM_MAPPINGS = (
        ('id', 'AssignmentId'),
        ('assignment_status', 'AssignmentStatus',
            lambda f, D=assignment_status_key_to_str: D[f],
            lambda p, D=assignment_status_str_to_key: D[p]),
        ('worker', 'WorkerId',
            lambda f: f.id,
            lambda p: MturkWorker.objects.get(id=p)),
        ('hit', 'HITId',
            lambda f: f.id,
            lambda p: MturkHit.objects.get(id=p)),
        ('auto_approval_time', 'AutoApprovalTime'),
        ('accept_time', 'AcceptTime'),
        ('submit_time', 'SubmitTime'),
        ('approval_time', 'ApprovalTime'),
        ('rejection_time', 'RejectionTime'),
        ('deadline', 'Deadline'),
        ('answer_xml', 'Answer'),
        ('requester_feedback', 'RequesterFeedback')
    )

    def approve(self, feedback=None, override_rejection=False):
        params = {
            'AssignmentId': self.id,
            'OverrideRejection': override_rejection
        }
        if feedback is not None:
            params['RequesterFeedback'] = feedback
        get_mturk_client().approve_assignment(**params)
        print('Assignment {} is approved'.format(self.id))

    def reject(self, feedback=None):
        params = {
            'AssignmentId': self.id,
        }
        if feedback is not None:
            params['RequesterFeedback'] = feedback
        get_mturk_client().reject_assignment(**params)
        print('Assignment {} is rejected'.format(self.id))

    def save(self, *args, **kwargs):
        if self.id == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            print('AssignmentId is ASSIGNMENT_ID_NOT_AVAILABLE, pass.')
            return
        super(MturkAssignment, self).save(*args, **kwargs)

    @classmethod
    def create_or_update_from_response(cls, response):
        try:
            assignment = cls.objects.get(id=response['AssignmentId'])
        except cls.DoesNotExist:
            assignment = cls()
        
        # create worker object if new MTurk worker comes in
        MturkWorker.objects.get_or_create(id=response['WorkerId'])

        set_fields_from_params(
            assignment, response, assignment.FIELD_PARAM_MAPPINGS,
            ('id', 'worker', 'hit', 'assignment_status',
            'auto_approval_time', 'accept_time', 'submit_time', 'approval_time',
            'rejection_time', 'deadline', 'answer_xml', 'requester_feedback')
        )

        assignment.save()
        return assignment

    def __str__(self):
        return str(self.id)


class QualificationType(ModelBase):
    QUALIFICATION_TYPE_STATUS_CHOICES = (
        ('A', 'Active'),
        ('I', 'Inactive'),
    )
    qtype_status_key_to_str = dict((k,v) for (k,v) in QUALIFICATION_TYPE_STATUS_CHOICES)
    qtype_status_str_to_key = dict((v,k) for (k,v) in QUALIFICATION_TYPE_STATUS_CHOICES)

    id                 = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)
    creation_time      = models.DateTimeField()
    name               = models.CharField(max_length=64)
    keywords           = models.CharField(max_length=256)
    description        = models.TextField()
    qtype_status       = models.CharField(max_length=1, choices=QUALIFICATION_TYPE_STATUS_CHOICES, default='A')
    test               = models.TextField(null=True)
    test_duration      = models.DurationField(null=True)
    answer_key         = models.TextField(null=True)
    retry_delay        = models.DurationField(null=True)
    is_requestable     = models.BooleanField()
    auto_granted       = models.BooleanField()
    auto_granted_value = models.IntegerField(blank=True, null=True)

    slug = models.CharField(max_length=128, unique=True)

    FIELD_PARAM_MAPPINGS = (
        ('id', 'QualificationTypeId'),
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

    def associate_to_worker(self, worker, value=None, send_notification=False):
        params = {
            'QualificationTypeId': self.id,
            'WorkerId': worker.id,
            'SendNotification': send_notification
        }
        if value is not None:
            params['IntegerValue'] = value
        get_mturk_client().associate_qualification_with_worker(**params)
        print('QualificationType {} associated to worker {} with value {}. Notification{} sent'.format(
            self.id, worker, value, "" if send_notification else " not"
        ))
    
    def disassociate_from_worker(self, worker, reason=None):
        client = client or get_mturk_client()
        params = {
            'QualificationTypeId': self.id,
            'WorkerId': worker.id
        }
        if reason is not None:
            params['Reason'] = reason
        client.disassociate_qualification_from_worker(**params)
        print('QualificationType {} disassociated from worker {}'.format(self.id, worker))

    def save(self, update_on_mturk=True, *args, **kwargs):
        if not self.id: # ID is None or empty string
            # create QualificationType on MTurk
            params = get_params_from_fields(
                self, self.FIELD_PARAM_MAPPINGS,
                ('name', 'keywords', 'description', 'qtype_status', 'retry_delay',
                 'test', 'test_duration', 'auto_granted', 'answer_key', 'auto_granted_value'),
                skip_none=True
            )
            response = get_mturk_client().create_qualification_type(**params)['QualificationType']
            print('QualificationType {} created on MTurk'.format(response['QualificationTypeId']))
            set_fields_from_params(
                self, response, self.FIELD_PARAM_MAPPINGS,
                ('id', 'creation_time', 'qtype_status', 'is_requestable')
            )
        else:
            # update QualificationType on Mturk
            if update_on_mturk:
                params = get_params_from_fields(
                    self, self.FIELD_PARAM_MAPPINGS,
                    ('id', 'description', 'qtype_status', 'test', 'answer_key',
                    'test_duration', 'retry_delay', 'auto_granted', 'auto_granted_value'),
                    skip_none=True
                )
                get_mturk_client().update_qualification_type(**params)
                print('QualificationType {} updated on MTurk'.format(self.id))

        super(QualificationType, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        get_mturk_client().delete_qualification_type(
            QualificationTypeId=self.id
        )
        print('QualificationType {} deleted on MTurk'.format(self.id))
        super(QualificationType, self).delete(*args, **kwargs)

    def sync_requests(self, sync_workers=True):
        assert(sync_workers == True)
        page_size = 64

        # retrieve all requests
        qrequest_responses = []
        response = get_mturk_client().list_qualification_requests(
            QualificationTypeId=self.id,
            MaxResults=page_size
        )
        print(response)
        qrequest_responses.extend(response['QualificationRequests'])
        while 'NextToken' in response:
            response = get_mturk_client().list_qualification_requests(
                QualificationTypeId=self.id,
                NextToken=response['NextToken'],
                MaxResults=page_size
            )
            qrequest_responses.extend(response['QualificationRequests'])

        for request in qrequest_responses:
            assert(self.id == request['QualificationTypeId'])
            worker, _ = MturkWorker.get_or_create(id=request['WorkerId'])
            qrequest, created = QualificationRequest.get_or_create(
                id          = request['QualificationRequestId'],
                qtype       = self,
                worker      = worker,
                test        = request['Test'],
                answer      = request['Answer'],
                submit_time = request['SubmitTime']
            )
            print('QualificationRequest {} {}'.format(qrequest, 'created' if created else 'exists'))

    def sync(self, sync_requests=True):
        """ Sync status and its requests """
        # sync QualificationType status with MTurk
        response = get_mturk_client().get_qualification_type(
            QualificationTypeId=self.id
        )['QualificationType']
        set_fields_from_params(
            self, response, self.FIELD_PARAM_MAPPINGS,
            ('qtype_status', 'is_requestable'))
        self.save(update_on_mturk=False)

        if sync_requests == True:
            self.sync_requests()

    def __str__(self):
        return self.slug


class QualificationRequest(ModelBase):
    """QualificationRequest should be created by calling QualificationType.sync_requests"""

    id          = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)
    qtype       = models.ForeignKey(QualificationType, related_name='requests')
    worker      = models.ForeignKey(MturkWorker, related_name='requests')
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
        return str(self.id)
