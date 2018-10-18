from django.template.loader import get_template
from django.test import TestCase

# Create your tests here.
from dateutil.parser import parse as parse_time

from wechat.models import User, Activity, Ticket
from wechat.testclientlib import WechatTestClientLib
from wechat.views import CustomWeChatView


class WechatBaseTest(TestCase):
    def setUp(self):
        User.objects.create(
            open_id='921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A',
            student_id='2016012345'
        ).save()
        User.objects.create(
            open_id='B72AAF5F26554351B768642D7618ECCE42EA2BEEA9DE4B108E59744CFC028044'
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

        self.activity_map = {
            '7e': activity_7e,
            '8d': activity_8d,
            '21': activity_21
        }

        self.wechat_server = WechatTestClientLib()

    def tearDown(self):
        User.objects.all().delete()
        Activity.objects.all().delete()
        Ticket.objects.all().delete()


class BookWhatTest(WechatBaseTest):

    def test_not_bind_user_can_see(self):
        self.wechat_server.mock_timezone_now(parse_time('2018-10-19 00:59:59 UTC'))  # right before the ddl
        resp = self.wechat_server.send_click(CustomWeChatView.event_keys['book_what'],
                                             'B72AAF5F26554351B768642D7618ECCE42EA2BEEA9DE4B108E59744CFC028044')
        self.assertEqual(self.wechat_server.get_msg_type(resp), 'news', 'book what reply not news')
        news = self.wechat_server.get_news(resp)
        self.assertEqual(len(news), 1, 'wrong news count: {}'.format(len(news)))
        self.assertEqual(news[0]['Title'], get_template('messages/activity_title.html').render({
            'activity': self.activity_map['7e']
        }), 'news title mismatch: {}'.format(news[0]['Title']))

    def test_after_ddl_cannot_see(self):
        self.wechat_server.mock_timezone_now(parse_time('2018-10-19 01:00:00 UTC'))  # right after the ddl
        resp = self.wechat_server.send_click(CustomWeChatView.event_keys['book_what'],
                                             'B72AAF5F26554351B768642D7618ECCE42EA2BEEA9DE4B108E59744CFC028044')
        self.assertEqual(self.wechat_server.get_msg_type(resp), 'text', 'reply not text')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/book_empty.html').render(),
                         'now should have no activity to snap up')

    def test_close_activity_cannot_see(self):
        self.activity_map['7e'].status = Activity.STATUS_DELETED
        self.activity_map['7e'].save()

        self.wechat_server.mock_timezone_now(parse_time('2018-10-19 00:59:59 UTC'))  # right before the ddl
        resp = self.wechat_server.send_click(CustomWeChatView.event_keys['book_what'],
                                             '12345')
        self.assertEqual(self.wechat_server.get_msg_type(resp), 'text', 'reply not text')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/book_empty.html').render(),
                         'now should have no activity to snap up')

        self.activity_map['7e'].status = Activity.STATUS_PUBLISHED
        self.activity_map['7e'].save()


class SnapUpTicketTest(WechatBaseTest):
    def setUp(self):
        super().setUp()
        self.activity_map['7e'].remain_tickets = 1
        self.activity_map['7e'].save()

    def test_before_start_book(self):
        self.wechat_server.mock_timezone_now(parse_time('2018-10-18 23:59:59 UTC'))
        resp = self.wechat_server.send_click(
            CustomWeChatView.event_keys['book_header'] + str(self.activity_map['7e'].id),
            '48A3CB2513F049A98A7DFD2453ED717296F3D2B76DC7407DB3886D5F4F4B5C04')
        self.assertEqual(self.wechat_server.get_msg_type(resp), 'text')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/book_not_start.html').render(),
                         'cannot book before start_book time')

    def test_after_start_book(self):
        self.wechat_server.mock_timezone_now(parse_time('2018-10-19 00:00:00 UTC'))
        resp = self.wechat_server.send_text(
            '抢票  ' + self.activity_map['7e'].key,
            '48A3CB2513F049A98A7DFD2453ED717296F3D2B76DC7407DB3886D5F4F4B5C04')

        self.assertEqual(self.wechat_server.get_msg_type(resp), 'news')
        news = self.wechat_server.get_news(resp)
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0]['Description'], get_template('messages/book_ticket_success_detail.html').render({
            'activity': self.activity_map['7e']
        }), 'should success after book_start')

        # restore
        self.wechat_server.send_text('退票 ' + self.activity_map['7e'].key,
                                     '48A3CB2513F049A98A7DFD2453ED717296F3D2B76DC7407DB3886D5F4F4B5C04')

    def test_before_book_end(self):
        self.wechat_server.mock_timezone_now(parse_time('2018-10-19 01:00:00 UTC'))
        resp = self.wechat_server.send_click(
            CustomWeChatView.event_keys['book_header'] + str(self.activity_map['7e'].id),
            '48A3CB2513F049A98A7DFD2453ED717296F3D2B76DC7407DB3886D5F4F4B5C04')

        self.assertEqual(self.wechat_server.get_msg_type(resp), 'news')
        news = self.wechat_server.get_news(resp)
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0]['Description'], get_template('messages/book_ticket_success_detail.html').render({
            'activity': self.activity_map['7e']
        }), 'should success before book_end')

        # restore
        self.wechat_server.send_text('退票 ' + self.activity_map['7e'].key,
                                     '48A3CB2513F049A98A7DFD2453ED717296F3D2B76DC7407DB3886D5F4F4B5C04')

    def test_after_book_end(self):
        self.wechat_server.mock_timezone_now(parse_time('2018-10-19 01:00:01 UTC'))
        resp = self.wechat_server.send_text(
            '抢票  ' + self.activity_map['7e'].key,
            '48A3CB2513F049A98A7DFD2453ED717296F3D2B76DC7407DB3886D5F4F4B5C04')
        self.assertEqual(self.wechat_server.get_msg_type(resp), 'text')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/book_end_already.html').render(),
                         'cannot book after book_end time')

    def test_user_not_bind(self):
        self.wechat_server.mock_timezone_now(parse_time('2018-10-19 00:00:00 UTC'))
        resp = self.wechat_server.send_text(
            '抢票  ' + self.activity_map['7e'].key,
            'B72AAF5F26554351B768642D7618ECCE42EA2BEEA9DE4B108E59744CFC028044')

        self.assertEqual(self.wechat_server.get_msg_type(resp), 'text')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/id_not_bind.html').render())

        self.wechat_server.mock_timezone_now(parse_time('2018-10-19 00:00:00 UTC'))
        resp = self.wechat_server.send_click(
            CustomWeChatView.event_keys['book_header'] + str(self.activity_map['7e'].id),
            '23456')

        self.assertEqual(self.wechat_server.get_msg_type(resp), 'text')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/id_not_bind.html').render())

    def test_ticket_sold_out(self):
        self.wechat_server.mock_timezone_now(parse_time('2018-10-19 01:00:00 UTC'))
        resp = self.wechat_server.send_text('抢票 ' + self.activity_map['7e'].key,
                                            '48A3CB2513F049A98A7DFD2453ED717296F3D2B76DC7407DB3886D5F4F4B5C04')
        news = self.wechat_server.get_news(resp)
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0]['Description'], get_template('messages/book_ticket_success_detail.html').render({
            'activity': self.activity_map['7e']
        }), '1 ticket remain, snap up should succeed')

        resp = self.wechat_server.send_text('抢票 ' + self.activity_map['7e'].key,
                                            '48A3CB2513F049A98A7DFD2453ED717296F3D2B76DC7407DB3886D5F4F4B5C04')
        news = self.wechat_server.get_news(resp)
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0]['Description'], get_template('messages/withdraw_ticket_detail.html').render({
            'activity': self.activity_map['7e']
        }), 'although no ticket left, booked user should give him ticket')

        resp = self.wechat_server.send_text('抢票 ' + self.activity_map['7e'].key,
                                            '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/sold_out.html').render(),
                         'no ticket, other user should fail')

        # restore
        self.wechat_server.send_text('退票' + self.activity_map['7e'].key,
                                     '48A3CB2513F049A98A7DFD2453ED717296F3D2B76DC7407DB3886D5F4F4B5C04')

    def test_invalid_activity_id(self):
        self.wechat_server.mock_timezone_now(parse_time('2018-10-19 01:00:00 UTC'))
        resp = self.wechat_server.send_click(CustomWeChatView.event_keys['book_header'] + 'aaa',
                                             '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/activity_not_found.html').render(),
                         'invalid activity id should end decently')

        resp = self.wechat_server.send_click(
            CustomWeChatView.event_keys['book_header'] + str(self.activity_map['8d'].id),
            '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/activity_not_found.html').render(),
                         'invalid activity id should end decently')

        resp = self.wechat_server.send_click(
            CustomWeChatView.event_keys['book_header'] + str(self.activity_map['21'].id),
            '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/activity_not_found.html').render(),
                         'invalid activity id should end decently')

        resp = self.wechat_server.send_text('抢票 ' + self.activity_map['8d'].key,
                                            '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/activity_not_found.html').render(),
                         'invalid activity id should end decently')

        resp = self.wechat_server.send_text('抢票 ' + 'WtfTicket',
                                            '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/activity_not_found.html').render(),
                         'invalid activity id should end decently')


class CancelTicketTest(WechatBaseTest):
    def setUp(self):
        super().setUp()
        self.activity_map['7e'].remain_tickets = 1
        self.activity_map['7e'].save()

    def test_user_not_bind(self):
        self.wechat_server.mock_timezone_now(parse_time('2018-10-19 00:00:00 UTC'))
        resp = self.wechat_server.send_text(
            '退票  ' + self.activity_map['7e'].key,
            'B72AAF5F26554351B768642D7618ECCE42EA2BEEA9DE4B108E59744CFC028044')

        self.assertEqual(self.wechat_server.get_msg_type(resp), 'text')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/id_not_bind.html').render())

    def test_cancel_used_canceled_ticket(self):
        self.wechat_server.mock_timezone_now(parse_time('2018-10-19 00:00:00 UTC'))
        resp = self.wechat_server.send_text(
            '抢票  ' + self.activity_map['7e'].key,
            '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A')
        news = self.wechat_server.get_news(resp)
        self.assertEqual(len(news), 1)
        ticket = Ticket.objects.filter(student_id='2016012345', activity=self.activity_map['7e'],
                                       status=Ticket.STATUS_VALID).first()
        self.assertIsNotNone(ticket)

        ticket.status = Ticket.STATUS_USED
        ticket.save()
        resp = self.wechat_server.send_text(
            '退票  ' + self.activity_map['7e'].key,
            '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/no_ticket_in_hand.html').render())

        ticket.status = Ticket.STATUS_USED
        ticket.save()
        resp = self.wechat_server.send_text(
            '退票  ' + self.activity_map['7e'].key,
            '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/no_ticket_in_hand.html').render())

        ticket.status = Ticket.STATUS_CANCELLED
        ticket.save()
        resp = self.wechat_server.send_text(
            '退票  ' + self.activity_map['7e'].key,
            '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/no_ticket_in_hand.html').render())

        ticket.status = Ticket.STATUS_VALID
        ticket.save()
        resp = self.wechat_server.send_text(
            '退票  ' + self.activity_map['7e'].key,
            '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/cancel_complete.html').render({
            'activity': self.activity_map['7e']
        }))

    def test_cancel_snap_up_repeat(self):
        user_a = '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A'
        user_b = '48A3CB2513F049A98A7DFD2453ED717296F3D2B76DC7407DB3886D5F4F4B5C04'
        act = self.activity_map['7e']

        # user a snap up
        resp = self.wechat_server.send_click(CustomWeChatView.event_keys['book_header'] + str(act.id), user_a)
        news = self.wechat_server.get_news(resp)
        self.assertEqual(len(news), 1)

        # user a cancel
        resp = self.wechat_server.send_text('退票 ' + act.key, user_a)
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/cancel_complete.html').render({
            'activity': act
        }))

        # user a snap up again
        resp = self.wechat_server.send_click(CustomWeChatView.event_keys['book_header'] + str(act.id), user_a)
        news = self.wechat_server.get_news(resp)
        self.assertEqual(len(news), 1)

        # user a cancel again
        resp = self.wechat_server.send_text('退票 ' + act.key, user_a)
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/cancel_complete.html').render({
            'activity': act
        }))

        # user b snap up
        resp = self.wechat_server.send_text('抢票 ' + act.key, user_b)
        news = self.wechat_server.get_news(resp)
        self.assertEqual(len(news), 1)

        # user b cancel
        resp = self.wechat_server.send_text('退票 ' + act.key, user_b)
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/cancel_complete.html').render({
            'activity': act
        }))


class LookUpTicketTest(WechatBaseTest):

    def test_user_not_bind(self):
        self.wechat_server.mock_timezone_now(parse_time('2018-10-19 00:00:00 UTC'))
        resp = self.wechat_server.send_click(CustomWeChatView.event_keys['get_ticket'],
                                             'B72AAF5F26554351B768642D7618ECCE42EA2BEEA9DE4B108E59744CFC028044')

        self.assertEqual(self.wechat_server.get_msg_type(resp), 'text')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/id_not_bind.html').render())

    def test_user_has_deleted_activity_ticket(self):
        user_open_id = '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A'
        user_student_id = '2016012345'
        Ticket.create_ticket(
            student_id=user_student_id,
            activity=self.activity_map['7e']
        )
        Ticket.create_ticket(  # others' ticket
            student_id='2018000000',
            activity=self.activity_map['7e']
        )
        Ticket.create_ticket(
            student_id=user_student_id,
            activity=self.activity_map['8d']
        )
        Ticket.create_ticket(
            student_id=user_student_id,
            activity=self.activity_map['21']
        )

        resp = self.wechat_server.send_click(CustomWeChatView.event_keys['get_ticket'], user_open_id)
        news = self.wechat_server.get_news(resp)
        self.assertEqual(len(news), 1, 'deleted or saved activities\' tickets would not be included')
        self.assertEqual(news[0]['Title'], get_template('messages/ticket_title.html').render({
            'activity': self.activity_map['7e']
        }))

        # restore
        Ticket.objects.all().delete()

    def test_user_no_ticket_at_all(self):
        user_open_id = '921E1460FD86481C9087C7E2A9B7C6322967F79BDFC34ED2873EFC8106EDC38A'

        resp = self.wechat_server.send_click(CustomWeChatView.event_keys['get_ticket'], user_open_id)
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/ticket_empty.html').render())


class WithdrawTicketTest(WechatBaseTest):

    def setUp(self):
        super().setUp()
        self.activity_map['7e'].remain_tickets = 1
        self.activity_map['7e'].save()

    def test_user_not_bind(self):
        self.wechat_server.mock_timezone_now(parse_time('2018-10-19 00:00:00 UTC'))
        resp = self.wechat_server.send_text('取票 ' + self.activity_map['7e'].key,
                                            'B72AAF5F26554351B768642D7618ECCE42EA2BEEA9DE4B108E59744CFC028044')

        self.assertEqual(self.wechat_server.get_msg_type(resp), 'text')
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/id_not_bind.html').render())

    def test_user_have_ticket(self):
        user_open_id = '48A3CB2513F049A98A7DFD2453ED717296F3D2B76DC7407DB3886D5F4F4B5C04'
        act = self.activity_map['7e']

        resp = self.wechat_server.send_text('取票 ' + self.activity_map['7e'].key, user_open_id)
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/no_ticket_in_hand.html').render())

        self.wechat_server.send_text('抢票 ' + self.activity_map['7e'].key, user_open_id)
        resp = self.wechat_server.send_text('取票 ' + self.activity_map['7e'].key, user_open_id)
        news = self.wechat_server.get_news(resp)
        self.assertEqual(len(news), 1)
        self.assertEqual(news[0]['Title'], get_template('messages/withdraw_ticket_title.html').render())
        self.assertEqual(news[0]['Description'], get_template('messages/withdraw_ticket_detail.html').render({
            'activity': act
        }))

        self.wechat_server.send_text('退票 ' + self.activity_map['7e'].key, user_open_id)
        resp = self.wechat_server.send_text('取票 ' + self.activity_map['7e'].key, user_open_id)
        self.assertEqual(self.wechat_server.get_text(resp), get_template('messages/no_ticket_in_hand.html').render())
