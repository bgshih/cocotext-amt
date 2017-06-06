import json

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.core.serializers.json import DjangoJSONEncoder

MAX_ID_LENGTH = 128
MAX_CATEGORY_NAME_LENGTH = 128
MAX_TEXT_LENGTH = 10485760 # 10MB


class Experiment(models.Model):
    name = models.CharField(max_length=64)
    version = models.CharField(max_length=16, default='0.0.1')

    # HIT settings
    max_assignments                = models.PositiveSmallIntegerField(default=1)
    auto_approval_delay_in_seconds = models.PositiveIntegerField(default=3600*24*14)
    lifetime_in_seconds            = models.PositiveIntegerField(default=3600*24*30)
    assignment_duration_in_seconds = models.PositiveIntegerField(default=3600)
    reward                         = models.DecimalField(decimal_places=4, max_digits=8)
    title                          = models.CharField(max_length=256)
    keywords                       = models.CharField(max_length=256)
    description                    = models.CharField(max_length=4096)
    question                       = models.CharField(max_length=10*1024*1024)

    def __str__(self):
        return self.name


################################################
# MTurk Objects
################################################

class MturkWorker(models.Model):
    # obtained from AMT
    worker_id = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)

    def __str__(self):
        return self.worker_id

def get_or_create_worker(worker_id, save=True):
    try:
        worker = MturkWorker.objects.get(pk=worker_id)
    except MturkWorker.DoesNotExist:
        worker = MturkWorker()
        worker.worker_id = worker_id
    worker.save()
    return worker


class MturkHit(models.Model):
    experiment = models.ForeignKey(Experiment, related_name='hits')

    # obtained from AMT after HIT creation
    hit_id        = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)
    hit_type_id   = models.CharField(max_length=MAX_ID_LENGTH)
    hit_group_id  = models.CharField(max_length=MAX_ID_LENGTH)
    creation_time = models.DateTimeField()
    expiration    = models.DateTimeField()

    HIT_STATUS_CHOICES = (
        ('A', 'Assignable'),
        ('U', 'Unassignable'),
        ('R', 'Reviewable'),
        ('E', 'Reviewing'),
        ('D', 'Disposed'),
    )
    str_to_hit_status = dict((v, k) for (k, v) in HIT_STATUS_CHOICES)
    hit_status_to_str = dict((k, v) for (k, v) in HIT_STATUS_CHOICES)
    hit_status = models.CharField(max_length=1,
                                  choices=HIT_STATUS_CHOICES)

    REVIEW_STATUS_CHOICES = (
        ('N', 'NotReviewed'),
        ('M', 'MarkedForReview'),
        ('A', 'ReviewedAppropriate'),
        ('I', 'ReviewedInappropriate')
    )
    str_to_review_status = dict((v, k) for (k, v) in REVIEW_STATUS_CHOICES)
    review_status_to_str = dict((k, v) for (k, v) in REVIEW_STATUS_CHOICES)
    hit_review_status = models.CharField(max_length=1
                                         choices=REVIEW_STATUS_CHOICES)

    num_assignments_pending   = models.PositiveSmallIntegerField()
    num_assignments_available = models.PositiveSmallIntegerField()
    num_assignments_completed = models.PositiveSmallIntegerField()

    def save(self, *args, **kwargs):
        if not self.hit_id:
            # create HIT
            response = get_mturk_client().create_hit(
                MaxAssignments              = self.experiment.max_assignments,
                AutoApprovalDelayInSeconds  = self.experiment.auto_approval_delay_in_seconds,
                LifetimeInSeconds           = self.experiment.lifetime_in_seconds,
                AssignmentDurationInSeconds = self.experiment.assignment_duration_in_seconds,
                Reward                      = str(self.experiment.reward),
                Title                       = self.experiment.title,
                Keywords                    = self.experiment.keywords,
                Description                 = self.experiment.description,
                Question                    = self.experiment.question
                # RequesterAnnotation is not used
                # QualificationRequirements TODO
                # UniqueRequestToken is not used
                # AssignmentReviewPolicy is not used
                # HITReviewPolicy is not used
                # HITLayoutId is not used
                # HITLayoutParameters is not used
            )
            )['HIT']

            self.hit_id                    = response['HITId']
            self.hit_type_id               = response['HITTypeId']
            self.hit_group_id              = response['HITGroupId']
            self.hit_layout_id             = response['HITLayoutId']
            self.creation_time             = response['CreationTime']
            self.expiration                = response['Expiration']
            self.hit_status                = str_to_hit_status(response['HITStatus'])
            self.review_status             = str_to_review_status(response['HITReviewStatus'])
            self.num_assignments_pending   = response['NumberOfAssignmentsPending']
            self.num_assignments_available = response['NumberOfAssignmentsAvailable']
            self.num_assignments_completed = response['NumberOfAssignmentsCompleted']

        super(MtHit, self).save(*args, **kwargs)

    def sync(self, sync_assignments=True):
        """ Sync status with AMT, also sync its assignments """
        client = get_mturk_client()
        response = client.get_hit(HITId=self.hit_id)['HIT']

        self.hit_status                = str_to_hit_status(response['HITStatus'])
        self.review_status             = str_to_review_status(response['HITReviewStatus'])
        self.num_assignments_pending   = response['NumberOfAssignmentsPending']
        self.num_assignments_available = response['NumberOfAssignmentsAvailable']
        self.num_assignments_completed = response['NumberOfAssignmentsCompleted']

        self.save()

        # update all assignments
        if sync_assignments:
            response = client.list_assignments_for_hit(
                HITId=self.hit_id,
                MaxResults=100, # assignments should never exceed 100
                AssignmentStatuses=['Submitted', 'Approved', 'Rejected']
            )['Assignments']
            for assignment_response in response:
                create_or_update_assignment(assignment_response)

    def __str__(self):
        return self.hit_id


class MturkAssignment(models.Model):
    assignment_id = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)
    worker        = models.ForeignKey(MturkWorker, related_name='assignments')
    hit           = models.ForeignKey(MturkHit, related_name='assignments')

    ASSIGNMENT_STATUS_CHOICES = (
        ('S', 'Submitted'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
    )
    assignment_status = models.CharField(max_length=1,
                                         choices=ASSIGNMENT_STATUS_CHOICES)
    
    auto_approval_time = models.DateTimeField()
    accept_time        = models.DateTimeField()
    submit_time        = models.DateTimeField()
    approval_time      = models.DateTimeField()
    rejection_time     = models.DateTimeField()
    deadline           = models.DateTimeField()
    answer             = JSONField()

    def save(self, *args, **kwargs):
        if self.assignment_id == 'ASSIGNMENT_ID_NOT_AVAILABLE':
            return
        super(MtAssignment, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.assignment_id)

def create_or_update_assignment(response, save=True):
    try:
        assignment = MturkAssignment.objects.get(pk=response['AssignmentId'])
    except MturkAssignment.DoesNotExist:
        assignment = MturkAssignment()

    assignment.assignment_id      = response['AssignmentId']
    assignment.worker             = get_or_create_worker(response['WorkerId'])
    assignment.hit_id             = response['HITId']
    assignment.assignment_status  = response['AssignmentStatus']
    assignment.auto_approval_time = response['AutoApprovalTime']
    assignment.accept_time        = response['AcceptTime']
    assignment.submit_time        = response['SubmitTime']
    assignment.approval_time      = response['ApprovalTime']
    assignment.rejection_time     = response['RejectionTime']
    assignment.deadline           = response['Deadline']

    try:
        answer_data = json.loads(response['Answer'])
    except ValueError:
        answer_data = {}
    assignment.answer = answer_data
    # RequesterFeedback is ignored
    
    if save:
        assignment.save()

    return assignment


################################################
# COCO-Text Objects
################################################

class CocoTextImage(models.Model):
    id     = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)
    width  = models.PositiveIntegerField()
    height = models.PositiveIntegerField()

    SUBSET_CHOICES = (
        ('TRN', 'Training'),
        ('VAL', 'Validation'),
        ('TST', 'Test'))
    subset = models.CharField(max_length=3, choices=SUBSET_CHOICES)

    def __str__(self):
        return str(self.id)


class CocoTextInstance(models.Model):
    id         = models.CharField(max_length=MAX_ID_LENGTH, primary_key=True)
    image      = models.ForeignKey(CocoTextImage, on_delete=models.CASCADE)
    polygon    = JSONField()
    text       = models.CharField(max_length=MAX_TEXT_LENGTH)
    legibility = models.CharField(max_length=MAX_CATEGORY_NAME_LENGTH)
    language   = models.CharField(max_length=MAX_CATEGORY_NAME_LENGTH)

    # Instance is inherited from V1
    from_v1     = models.BooleanField(default=False)

    # polygon annotation has been verified
    polygon_verified = models.BooleanField(default=False)

    # text annotation has been verified
    text_verified = models.BooleanField(default=False)

    # legibility has been verified
    legibility_verified = models.BooleanField(default=False)

    # language has been verified
    language_verified = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class CocoTextInstanceGroup(models.Model):
    image = models.ForeignKey(CocoTextImage, on_delete=models.CASCADE)
    # TODO


################################################
# HIT Contents
################################################

# class PolygonAnnotationTask(models.Model):
#     coco_image_id  = models.CharField(max_length=MAX_ID_LENGTH)
#     hints          = JSONField()
#     v1_annot_ids   = JSONField()
#     existing_annot = JSONField()
#     mturk_hit      = models.OneToOneField(MturkHit,
#                                           blank=True,
#                                           null=True,
#                                           on_delete=models.CASCADE,
#                                           related_name='polygon_annotation_task')

#     def __str__(self):
#         return str(self.id)


class PolygonVerificationTask(models.Model):
    # Each task is associated with one HIT
    mturk_hit = models.OneToOneField(MturkHit,
                                     blank=True,
                                     null=True,
                                     on_delete=models.CASCADE,
                                     related_name='polygon_verification_task')

    # tasks of a kind belong to an experiment
    experiment = models.ForeignKey(Experiment, related_name='polygon_verification_tasks')

    # A task verifies multiple instances, each instance is verified in multiple tasks
    text_instances = models.ManyToManyField(TextInstanceForPolygonVerification)

    def create_hit(self):
        hit = this.experiment.new_hit(save=True)
        self.mturk_hit = hit

    def save(self, create_hit=True, *args, **kwargs):
        if create_hit:
            self.create_hit()
        super(PolygonVerificationTask, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class TextInstanceForPolygonVerification(models.Model):
    """
    Submitted contents for PolygonAnnotationTask
    """
    text_instance = models.OneToOne(CocoTextInstance,
                                    related_name='text_instance_for_polygon_verification')

    # The assignments where this instance appears.
    # An instance may appear in multiple assignments
    assignments = models.ManyToMany(MturkAssignment,
                                    related_name='text_instances_for_polygon_verification')

    VERIFICATION_RESULT_CHOICES = (
        'CO': 'Correct',
        'WR': 'WRONG',
        'US': 'Unsure',
        'UV': 'Unverified'
    )
    verification_status = models.CharField(
        max_length=1,
        choices=VERIFICATION_RESULT_CHOICES,
        default='UV'
    )

    def __str__(self):
        return str(self.id)
