from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import *
import time


class UserBind(APIView):

    def validate_user(self):
        """
        input: self.input['student_id'] and self.input['password']
        raise: ValidateError when validating failed
        """
        try:
            # to ensure user has a unique student_id,
            # if we find student_id has been bind,
            # raise ValidateError
            _ = User.get_by_student_id(self.input['student_id'])
        except LogicError:
            pass
        else:
            raise ValidateError('Same student_id has been used.')

    def get(self):
        self.check_input('openid')
        return User.get_by_openid(self.input['openid']).student_id

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()


class ActivityDetail(APIView):
    @staticmethod
    def make_detail(activity: Activity):
        return {
            'name': activity.name,
            'key': activity.key,
            'description': activity.description,
            'startTime': int(activity.start_time.timestamp()),
            'endTime': int(activity.end_time.timestamp()),
            'place': activity.place,
            'bookStart': int(activity.book_start.timestamp()),
            'bookEnd': int(activity.book_end.timestamp()),
            'totalTickets': activity.total_tickets,
            'picUrl': activity.pic_url,
            'remainTickets': activity.remain_tickets,
            'currentTime': int(time.time())
        }

    def get(self):
        self.check_input('id')
        activity_id = int(self.input['id'])
        activity = Activity.get_by_activity_id(activity_id)
        if activity.status == Activity.STATUS_PUBLISHED:
            return ActivityDetail.make_detail(activity)
        else:
            raise LogicError('Activity not published.')


class TicketDetail(APIView):
    @staticmethod
    def make_detail(ticket: Ticket):
        activity = ticket.activity
        return {
            'activityName': activity.name,
            'place': activity.place,
            'activityKey': activity.key,
            'uniqueId': ticket.unique_id,
            'startTime': int(activity.start_time.timestamp()),
            'endTime': int(activity.end_time.timestamp()),
            'currentTime': int(time.time()),
            'status': ticket.status
        }

    def get(self):
        self.check_input('openid', 'ticket')
        openid = self.input['openid']
        ticket_unique_id = self.input['ticket']
        ticket = Ticket.get_by_ticket_unique_id(ticket_unique_id)

        # check if owner of the ticket has same openid with the query
        owner_student_id = ticket.student_id
        owner_open_id = User.get_by_student_id(owner_student_id).open_id

        if owner_open_id == openid:
            return TicketDetail.make_detail(ticket)
        else:
            raise ValidateError('You don\'t have permission to view this ticket.')
