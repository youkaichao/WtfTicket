from django.test import TestCase, Client
from django.contrib.auth.models import User
from wechat.models import Activity
from codex.baseerror import *
import dateutil
import json

backendAPIs = [
    ['/api/a/login', 'post'],
    ['/api/a/login', 'get'],
    ['/api/a/logout', 'post'],
    ['/api/a/activity/list', 'get'],
    ['/api/a/activity/delete', 'post'],
    ['/api/a/activity/create', 'post'],
    ['/api/a/image/upload', 'post'],
    ['/api/a/activity/detail', 'get'],
    ['/api/a/activity/detail', 'post'],
    ['/api/a/activity/menu', 'get'],
    ['/api/a/activity/menu', 'post'],
    ['/api/a/activity/checkin', 'post'],
]

needAuthorizationAPIs = backendAPIs[1:]


# Create your tests here.
class BackendAPITest(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='a', password='b')
        user.save()

    def tearDown(self):
        for q in User.objects.all():
            q.delete()
        for q in Activity.objects.all():
            q.delete()

    def checkURL(self, client, url, method, data, expect_code):
        if method == 'get':
            response = client.__getattribute__(method)(url, data=data)
        else:
            response = client.__getattribute__(method)(url, data=data, content_type='application/json')
        content = json.loads(response.content.decode())
        self.assertEqual(content['code'], expect_code,
                         'the return code is %s for url %s, but the expect_code is %s' % (
                         content['code'], url, expect_code))
        return content

    def login(self, c: Client):
        # check successful login
        self.checkURL(c, '/api/a/login', 'post', {"username": "a", "password": "b"}, 0)

    def logout(self, c: Client):
        # check logout
        self.checkURL(c, '/api/a/logout', 'post', None, 0)

    def test_login_authorization(self):
        # some api can only be used when the user is logged in
        c = Client()
        for (api, method) in needAuthorizationAPIs:
            self.checkURL(c, api, method, None, ValidateError("").code)

    def test_login_and_logout(self):
        c = Client()
        # check successful login
        self.checkURL(c, '/api/a/login', 'post', {"username": "a", "password": "b"}, 0)
        # check login status
        self.checkURL(c, '/api/a/login', 'get', None, 0)
        # check logout
        self.checkURL(c, '/api/a/logout', 'post', None, 0)
        # check failed login
        self.checkURL(c, '/api/a/login', 'post', {"username": "a", "password": "c"}, ValidateError("").code)

    def test_activity(self):
        # create activity and modify it, get it, then check if they are the same and then delete it
        c = Client()
        self.login(c)
        currentTime = '2018-10-16 14:59:51'
        data = {
            'name': 'what',
            'key': 'no',
            'place': 'where',
            'description': 'haha',
            'picUrl': 'not found',
            'startTime': currentTime,
            'endTime': currentTime,
            'bookStart': currentTime,
            'bookEnd': currentTime,
            'totalTickets': 100,
            'status': Activity.STATUS_PUBLISHED
        }
        # create an activity
        content = self.checkURL(c, '/api/a/activity/create', 'post', data, 0)
        id = content['data']
        data['id'] = id
        # modify it
        data['name'] = 'haha'
        self.checkURL(c, '/api/a/activity/detail', 'post', data, 0)
        # then check it
        retrieved = self.checkURL(c, '/api/a/activity/detail', 'get', {'id': id}, 0)
        for x in data:
            if x == 'id':
                continue
            if x in ['startTime', 'endTime', 'bookStart', 'bookEnd']:
                # check time
                self.assertEqual(int(dateutil.parser.parse(currentTime).timestamp()), retrieved['data'][x])
            else:
                self.assertEqual(data[x], retrieved['data'][x])
        # delete it
        self.checkURL(c, '/api/a/activity/delete', 'post', {'id': id}, 0)

        self.logout(c)
