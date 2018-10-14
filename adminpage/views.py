from django.shortcuts import render
from django.contrib.auth import logout, authenticate, login
from codex.baseview import APIView
from wechat.models import Activity, Ticket
from codex.baseerror import ValidateError, InputError, LogicError
from dateutil.parser import parse as datetime_parse_func
from WeChatTicket import settings
from wechat.views import CustomWeChatView
import urllib.parse
import datetime
import hashlib
import time
import os


def require_logged_in(func):
    def new_func(self):
        if not self.request.user.is_authenticated():
            raise ValidateError("Not logged in.")
        else:
            return func(self)
    return new_func


class UserLogin(APIView):
    @require_logged_in
    def get(self):
        return 0

    def post(self):
        self.check_input('username', 'password')
        user = authenticate(
            username=self.input['username'], password=self.input['password'])
        if user and user.is_active:
            login(self.request, user)
            return 0
        else:
            raise ValidateError("Wrong username or password.")


class UserLogout(APIView):
    @require_logged_in
    def post(self):
        logout(self.request)
        return 0


class ActivityList(APIView):
    @require_logged_in
    def get(self):
        data = list(Activity.objects.all())
        return [{
            'id': x.id,
            'name': x.name,
            'description': x.description,
            'startTime': int(x.start_time.timestamp()),
            'endTime': int(x.end_time.timestamp()),
            'place': x.place,
            'bookStart': int(x.book_start.timestamp()),
            'bookEnd': int(x.book_end.timestamp()),
            'currentTime': int(time.time()),
            'status': x.status
        }
            for x in data]


class ActivityDelete(APIView):
    @require_logged_in
    def post(self):
        self.check_input('id')
        q = Activity.objects.get(id=self.input['id'])
        q.delete()
        return 0


class ActivityCreate(APIView):
    @require_logged_in
    def post(self):
        self.check_input('name', 'key', 'place', 'description', 'picUrl', 'startTime', 'endTime', 'bookStart',
                         'bookEnd', 'totalTickets', 'status')
# FIX ME: startTime and endTIme are not correctly checked.
        q = Activity(name=self.input['name'], key=self.input['key'], place=self.input['place'],
                     description=self.input['description'], pic_url=self.input['picUrl'],
                     start_time=self.input['startTime'], end_time=self.input['endTime'],
                     book_start=self.input['bookStart'], book_end=self.input['bookEnd'],
                     total_tickets=self.input['totalTickets'], status=self.input['status'])
        q.remain_tickets = q.total_tickets
        q.save()
        return q.id


class ImageUpload(APIView):
    @require_logged_in
    def post(self):
        self.check_input('image')
        image = self.input['image'][0]
        content = image.file.read()
        md5 = hashlib.md5(content).hexdigest()
        filename = md5 + '.' + image._name.split('.')[-1]
        with open(os.path.join(settings.STATIC_ROOT, 'img', filename), 'wb') as f:
            f.write(content)
        return urllib.parse.urljoin(urllib.parse.urljoin(settings.CONFIGS['SITE_DOMAIN'], settings.STATIC_URL), 'img/' + filename)


class ActivityDetail(APIView):
    @require_logged_in
    def get(self):
        self.check_input('id')
        x = Activity.objects.get(id=self.input['id'])
        return {
            'name': x.name,
            'key': x.key,
            'description': x.description,
            'startTime': int(x.start_time.timestamp()),
            'endTime': int(x.end_time.timestamp()),
            'place': x.place,
            'bookStart': int(x.book_start.timestamp()),
            'bookEnd': int(x.book_end.timestamp()),
            'totalTickets': x.total_tickets,
            'picUrl': x.pic_url,
            'bookedTickets': x.total_tickets - x.remain_tickets,
            'usedTickets': len([x for x in Ticket.objects.all() if x.status == Ticket.STATUS_USED]),
            'currentTime': int(time.time()),
            'status': x.status
        }

    @require_logged_in
    def post(self):
        # illegal input has been dealt with at the front end
        self.check_input('id', 'name', 'place', 'description', 'picUrl', 'startTime', 'endTime', 'bookStart',
                         'bookEnd', 'totalTickets', 'status')
        x = Activity.objects.get(id=self.input['id'])
        x.name = self.input['name']
        x.place = self.input['place']
        x.description = self.input['description']
        x.pic_url = self.input['picUrl']
        x.start_time = datetime_parse_func(self.input['startTime'])
        x.end_time = datetime_parse_func(self.input['endTime'])
        x.book_start = datetime_parse_func(self.input['bookStart'])
        x.book_end = datetime_parse_func(self.input['bookEnd'])
        x.total_tickets = self.input['totalTickets']
        x.status = self.input['status']
        x.save()


class ActivityMenu(APIView):
    @require_logged_in
    def get(self):
        buttons = CustomWeChatView.lib.get_wechat_menu()
        if not buttons:
            raise LogicError("Empty WeChat list.")
        names = [x['name'] for x in buttons]
        if "抢票" not in names:
            raise LogicError("No ticket menu.")
        index = names.index("抢票")
        already_in = [x['name'] for x in buttons[index]['sub_button']]
        data = list(Activity.objects.all())
        return [{
            'id': x.id,
            'name': x.name,
            'menuIndex': 0
        }
            for x in data if x.name not in already_in
        ]

    @require_logged_in
    def post(self):
        ids = self.input
        CustomWeChatView.update_menu([Activity.objects.get(id=x) for x in ids])


class ActivityCheckin(APIView):
    @require_logged_in
    def post(self):
        self.check_input('actId')
        if ('ticket' in self.input and 'studentId' in self.input) or ('ticket' not in self.input and 'studentId' not in self.input):
            raise InputError(
                "Ticket and student ID, you can provide and only provide one.")
        if 'ticket' in self.input:
            x = Ticket.objects.get(unique_id=self.input['ticket'])
        else:
            x = Ticket.objects.get(student_id=self.input['studentId'])
        if x.status != Ticket.STATUS_VALID:
            raise Exception('ticket already used' if x.status ==
                            Ticket.STATUS_USED else 'ticket already cancelled')
        x.status = Ticket.STATUS_USED
        x.save()
        return {
            'ticket': x.unique_id,
            'studentId': x.student_id
        }
