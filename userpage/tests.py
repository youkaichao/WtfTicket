from django.test import TestCase
from wechat.models import *
from dateutil.parser import parse as parse_time
from .views import ActivityDetail, TicketDetail
import json


# Create your tests here.
class UserPageTest(TestCase):
    def setUp(self):
        User.objects.create(
            open_id='921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A',
            student_id='2016012345'
        ).save()
        User.objects.create(
            open_id='B72AAF5F26554351B768642D7618ECCE42EA2BEEA9DE4B108E59744CFC028044',
            student_id=''
        ).save()
        User.objects.create(
            open_id='48A3CB2513F049A98A7DFD2453ED717296F3D2B76DC7407DB3886D5F4F4B5C04',
            student_id='2018000000'
        ).save()

        activity_7e = Activity.objects.create(
            name='7EFE715EE7794F7EB126B3FD68488DAC',
            key='01A3C86BEDB446C9A9241BC60A0E2D03',
            description='A677567881054DA794E7161D14ABEDCA',
            start_time=parse_time('2018-10-20 00:00:00 UTC'),
            end_time=parse_time('2018-10-20 01:00:00 UTC'),
            place='C52F1D33C55C492DA75A3E34D86C2B7F',
            book_start=parse_time('2018-10-19 00:00:00 UTC'),
            book_end=parse_time('2018-10-19 01:00:00 UTC'),
            total_tickets=100,
            status=Activity.STATUS_PUBLISHED,
            pic_url='84EEF463D9BB414E8A97B05E7E41161B',
            remain_tickets=50
        )
        activity_7e.save()
        activity_8d = Activity.objects.create(
            name='8D0ACAEE58204101BAD0A096EE86872B',
            key='8315A42B982A4F929E628C41730D464A',
            description='6902EC1DCB7F46998FB12A9D8E969702',
            start_time=parse_time('2018-10-21 00:00:00 UTC'),
            end_time=parse_time('2018-10-21 01:00:00 UTC'),
            place='38578B119A8147CF8CE57F25D1AF43DD',
            book_start=parse_time('2018-10-20 00:00:00 UTC'),
            book_end=parse_time('2018-10-20 01:00:00 UTC'),
            total_tickets=100,
            status=Activity.STATUS_DELETED,
            pic_url='3910D1D24E4F4150A216FFB2879B0EE6',
            remain_tickets=50
        )
        activity_8d.save()

        activity_21 = Activity.objects.create(
            name='2145D42C37104AFE84F853CE496FC8E8',
            key='0E97E0CADFCB4CA4AEB732C630FDBD37',
            description='F1B7A9670AAA4734ACA0EF817A56A756',
            start_time=parse_time('2018-10-23 00:00:00 UTC'),
            end_time=parse_time('2018-10-23 01:00:00 UTC'),
            place='58F6440A38B74E1A8FA80024FC7FE56B',
            book_start=parse_time('2018-10-23 00:00:00 UTC'),
            book_end=parse_time('2018-10-23 01:00:00 UTC'),
            total_tickets=100,
            status=Activity.STATUS_SAVED,
            pic_url='C57329AE335A4286A902198F04D54C2D',
            remain_tickets=50
        )
        activity_21.save()

        self.activity_id_map = {
            '7e': activity_7e.id,
            '8d': activity_8d.id,
            '21': activity_21.id
        }

        Ticket.objects.create(
            student_id='2016012345',
            unique_id='6131D02D549744E29D335CAC9E60FAB2',
            activity=activity_7e,
            status=Ticket.STATUS_VALID
        )
        Ticket.objects.create(
            student_id='2018000000',
            unique_id='D42789364EA04E228585AEE95562D487',
            activity=activity_8d,
            status=Ticket.STATUS_VALID
        )

    def test_user_bind_get_1(self):
        # query student_id with open_id
        resp = self.client.get('/api/u/user/bind', {
            'openid': '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A'
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content.decode())
        self.assertEqual(resp['code'], 0)
        self.assertEqual(resp['data'], '2016012345')

    def test_user_bind_get_2(self):
        # query empty student_id
        resp = self.client.get('/api/u/user/bind', {
            'openid': 'B72AAF5F26554351B768642D7618ECCE42EA2BEEA9DE4B108E59744CFC028044'
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content.decode())
        self.assertEqual(resp['code'], 0)
        self.assertEqual(resp['data'], '')

    def test_user_bind_get_3(self):
        # query with non-existing open_id should have error
        resp = self.client.get('/api/u/user/bind', {
            'openid': '32DA889D4F2C48FFAB8259A00BAA64AC2FFA5E4B2DEA42FDB2124C45141E7085'
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content.decode())
        self.assertNotEqual(resp['code'], 0)

    def test_user_bind_post_1(self):
        # bind with non-existing open_id, should raise error
        resp = self.client.post('/api/u/user/bind', {
            'openid': '2C967540F6A643EAB15D4E18707599CADE5AF17393A94BD5842E7202BE221594',
            'student_id': '2019000000',
            'password': 'monkey'
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content.decode())
        self.assertNotEqual(resp['code'], 0)

    def test_user_bind_post_2(self):
        # bind with existing open_id and non-existing student_id
        resp = self.client.post('/api/u/user/bind', {
            'openid': 'B72AAF5F26554351B768642D7618ECCE42EA2BEEA9DE4B108E59744CFC028044',
            'student_id': '2019000123',
            'password': 'monkey'
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content.decode())
        self.assertEqual(resp['code'], 0)

        self.assertEqual(
            User.get_by_openid('B72AAF5F26554351B768642D7618ECCE42EA2BEEA9DE4B108E59744CFC028044').student_id,
            '2019000123'
        )

    def test_user_bind_post_3(self):
        # bind with existing open_id and existing student_id
        resp = self.client.post('/api/u/user/bind', {
            'openid': 'B72AAF5F26554351B768642D7618ECCE42EA2BEEA9DE4B108E59744CFC028044',
            'student_id': '2016012345',
            'password': 'monkey'
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content.decode())
        self.assertEqual(resp['code'], 0)

        self.assertEqual(
            User.get_by_openid('B72AAF5F26554351B768642D7618ECCE42EA2BEEA9DE4B108E59744CFC028044').student_id,
            '2016012345'
        )

    def test_activity_detail_get_1(self):
        # get activity normally
        resp = self.client.get('/api/u/activity/detail', {'id': self.activity_id_map['7e']})
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content.decode())
        self.assertEqual(resp['code'], 0)
        real = ActivityDetail.make_detail(Activity.get_by_activity_id(self.activity_id_map['7e']))
        real['currentTime'] = None
        resp['data']['currentTime'] = None
        self.assertEqual(resp['data'], real)

    def test_activity_detail_get_2(self):
        # get non-existing activity
        resp = self.client.get('/api/u/activity/detail', {'id': -5})
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content.decode())
        self.assertNotEqual(resp['code'], 0)

    def test_activity_detail_get_3(self):
        # get existing activity with other status
        resp = self.client.get('/api/u/activity/detail', {'id': self.activity_id_map['8d']})
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content.decode())
        self.assertNotEqual(resp['code'], 0)

    def test_activity_detail_get_4(self):
        # get existing activity with other status
        resp = self.client.get('/api/u/activity/detail', {'id': self.activity_id_map['21']})
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content.decode())
        self.assertNotEqual(resp['code'], 0)

    def test_ticket_detail_get_1(self):
        # if the student has the ticket
        resp = self.client.get('/api/u/ticket/detail', {
            'openid': '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A',
            'ticket': '6131D02D549744E29D335CAC9E60FAB2'
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content.decode())
        self.assertEqual(resp['code'], 0)

        ticket = Ticket.get_by_ticket_unique_id('6131D02D549744E29D335CAC9E60FAB2')
        detail = TicketDetail.make_detail(ticket)
        detail['currentTime'] = None
        resp['data']['currentTime'] = None
        self.assertEqual(detail, resp['data'])

    def test_ticket_detail_get_2(self):
        # if the ticket doesn't exist
        resp = self.client.get('/api/u/ticket/detail', {
            'openid': '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A',
            'ticket': 'CB87F2E9949E499ABA8FC2B69529A127'
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content.decode())
        self.assertNotEqual(resp['code'], 0)

    def test_ticket_detail_get_3(self):
        # if the student doesn't have the ticket
        resp = self.client.get('/api/u/ticket/detail', {
            'openid': '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A',
            'ticket': 'D42789364EA04E228585AEE95562D487'
        })
        self.assertEqual(resp.status_code, 200)
        resp = json.loads(resp.content.decode())
        self.assertNotEqual(resp['code'], 0)

    def tearDown(self):
        User.objects.all().delete()
        Activity.objects.all().delete()
        Ticket.objects.all().delete()