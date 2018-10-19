import uuid

from django.db import models, transaction

from codex.baseerror import LogicError


class User(models.Model):
    open_id = models.CharField(max_length=64, unique=True, db_index=True)
    student_id = models.CharField(max_length=32, unique=False, db_index=True)

    @classmethod
    def get_by_openid(cls, openid):
        try:
            return cls.objects.get(open_id=openid)
        except cls.DoesNotExist:
            raise LogicError('User not found')

    @classmethod
    def get_by_student_id(cls, student_id):
        try:
            return cls.objects.get(student_id=student_id)
        except cls.DoesNotExist:
            raise LogicError('User not found')

    @classmethod
    def bind_user_and_openid(cls, student_id, open_id):
        with transaction.atomic():
            old_user = cls.objects.select_for_update().filter(student_id=student_id).first()
            if old_user is not None:
                return False  # already binded
            user = cls.objects.select_for_update().filter(open_id=open_id).first()
            if user is None:
                return False  # cannot find current user
            user.student_id = student_id
            user.save()
            return True  # success


class Activity(models.Model):
    name = models.CharField(max_length=128)
    key = models.CharField(max_length=64, db_index=True)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    place = models.CharField(max_length=256)
    book_start = models.DateTimeField(db_index=True)
    book_end = models.DateTimeField(db_index=True)
    total_tickets = models.IntegerField()
    status = models.IntegerField()
    pic_url = models.CharField(max_length=256)
    remain_tickets = models.IntegerField()

    STATUS_DELETED = -1
    STATUS_SAVED = 0
    STATUS_PUBLISHED = 1

    @classmethod
    def get_by_activity_id(cls, activity_id):
        try:
            return cls.objects.get(id=activity_id)
        except cls.DoesNotExist:
            raise LogicError('Activity not found')

    @classmethod
    def get_by_activity_key(cls, activity_key):
        try:
            return cls.objects.get(key=activity_key)
        except cls.DoesNotExist:
            raise LogicError('Activity not found')

    @classmethod
    def decrease_ticket_exclusive(cls, activity_id):
        with transaction.atomic():
            try:
                activity = cls.objects.select_for_update().get(id=activity_id)
            except cls.DoesNotExist:
                return False  # cannot find activity, book fail
            if activity.remain_tickets <= 0:
                return False  # no ticket remained
            activity.remain_tickets -= 1
            activity.save()
            return True  # book ticket success

    @classmethod
    def increase_ticket_exclusive(cls, activity_id):
        with transaction.atomic():
            try:
                activity = cls.objects.select_for_update().get(id=activity_id)
            except cls.DoesNotExist:
                return  # cannot find activity, book fail
            activity.remain_tickets += 1
            activity.save()


class Ticket(models.Model):
    student_id = models.CharField(max_length=32, db_index=True)
    unique_id = models.CharField(max_length=64, db_index=True, unique=True)
    activity = models.ForeignKey(Activity)
    status = models.IntegerField()

    STATUS_CANCELLED = 0
    STATUS_VALID = 1
    STATUS_USED = 2

    def assign_uuid(self):
        res = uuid.uuid3(uuid.NAMESPACE_URL, str(uuid.uuid4()) + str(self.id))
        self.unique_id = str(res)

    @classmethod
    def create_ticket(cls, student_id, activity):
        ticket = Ticket(student_id=student_id, activity=activity, status=Ticket.STATUS_VALID)  # default status is valid
        ticket.assign_uuid()
        ticket.save()
        return ticket

    @classmethod
    def get_by_ticket_unique_id(cls, ticket_unique_id):
        try:
            return cls.objects.get(unique_id=ticket_unique_id)
        except cls.DoesNotExist:
            raise LogicError('Ticket not found')
