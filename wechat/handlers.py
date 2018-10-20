# -*- coding: utf-8 -*-
#
import time

from django.utils import timezone

from codex.baseerror import LogicError
from wechat.models import Activity, Ticket
from wechat.wrapper import WeChatHandler

__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        self.user.student_id = ''
        self.user.save()
        return self.reply_text(self.get_message('unbind_account'))


class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


class SnapUpTicketHandler(WeChatHandler):

    def is_event_click_startswith(self, *event_keys):
        return self.is_msg_type('event') and (self.input['Event'] == 'CLICK') and any(
            self.input['EventKey'].startswith(event_key) for event_key in event_keys)

    def check(self):
        return self.is_text_command('抢票') or self.is_event_click_startswith(self.view.event_keys['book_header'])

    def get_activity(self):
        """
        note: command can be followed by ONE space and activity key
        :return: current activity id, int
        """
        if self.is_text_command('抢票'):
            text = self.extract_activity_name()
            return Activity.get_by_activity_key(text)
        else:
            key = self.input['EventKey']
            key = key[len(self.view.event_keys['book_header']):]
            if key.isdigit():
                activity_id = int(key)
                return Activity.get_by_activity_id(activity_id)
            else:
                raise LogicError('EventKey does not contain id')

    def get_current_time(self):
        """
        :return: current server time, type float
        """
        return timezone.now().timestamp()

    def handle(self):
        try:
            activity = self.get_activity()
            if activity.status != Activity.STATUS_PUBLISHED:
                raise LogicError('activity not published')
        except LogicError:
            return self.reply_text(self.get_message('activity_not_found'))

        if self.user.student_id == '':  # not bind yet
            return self.reply_text(self.get_message('id_not_bind'))

        old_ticket = Ticket.objects.filter(student_id=self.user.student_id, activity_id=activity.id,
                                           status=Ticket.STATUS_VALID).first()
        if old_ticket is not None:  # in fact, it is not snap up ticket, it is withdraw ticket
            return self.reply_single_news({
                'Title': self.get_message('withdraw_ticket_title'),
                'Description': self.get_message('withdraw_ticket_detail', activity=activity),
                'Url': self.url_ticket_detail(old_ticket),
                'PicUrl': activity.pic_url,
            })

        if self.get_current_time() < activity.book_start.timestamp():  # not start yet
            return self.reply_text(self.get_message('book_not_start'))

        if self.get_current_time() > activity.book_end.timestamp():  # end already
            return self.reply_text(self.get_message('book_end_already'))

        result = Activity.decrease_ticket_exclusive(activity.id)
        if not result:
            return self.reply_text(self.get_message('sold_out'))

        ticket = Ticket.create_ticket(student_id=self.user.student_id, activity=activity)
        return self.reply_single_news({
            'Title': self.get_message('book_ticket_success_title'),
            'Description': self.get_message('book_ticket_success_detail', activity=activity),
            'Url': self.url_ticket_detail(ticket),
            'PicUrl': activity.pic_url,
        })


class CancelTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text_command('退票')

    def handle(self):
        text = self.extract_activity_name()

        activity = Activity.objects.filter(key=text).first()
        if activity is None or activity.status != Activity.STATUS_PUBLISHED:
            return self.reply_text(self.get_message('cancel_activity_not_found'))

        if self.user.student_id == '':  # not bind yet
            return self.reply_text(self.get_message('id_not_bind'))

        ticket = Ticket.objects.filter(student_id=self.user.student_id, activity=activity,
                                       status=Ticket.STATUS_VALID).first()
        if ticket is None:
            return self.reply_text(self.get_message('no_ticket_in_hand'))

        Activity.increase_ticket_exclusive(activity.id)
        ticket.status = Ticket.STATUS_CANCELLED
        ticket.save()

        return self.reply_text(self.get_message('cancel_complete', activity=activity))


class WithdrawTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text_command('取票')

    def handle(self):
        text = self.extract_activity_name()

        activity = Activity.objects.filter(key=text).first()
        if activity is None or activity.status != Activity.STATUS_PUBLISHED:
            return self.reply_text(self.get_message('activity_not_found'))

        if self.user.student_id == '':  # not bind yet
            return self.reply_text(self.get_message('id_not_bind'))

        ticket = Ticket.objects.filter(student_id=self.user.student_id, activity=activity,
                                       status=Ticket.STATUS_VALID).first()
        if ticket is None:
            return self.reply_text(self.get_message('no_ticket_in_hand'))

        return self.reply_single_news({
            'Title': self.get_message('withdraw_ticket_title'),
            'Description': self.get_message('withdraw_ticket_detail', activity=activity),
            'Url': self.url_ticket_detail(ticket),
            'PicUrl': activity.pic_url,
        })


class BookWhatHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_what'])

    def handle(self):
        activities = Activity.objects.filter(
            status=Activity.STATUS_PUBLISHED, book_end__gt=timezone.now()
        ).order_by('book_end')

        articles = []
        for activity in activities:
            articles.append({
                'Title': self.get_message('activity_title', activity=activity),
                'Description': self.get_message('activity_description', activity=activity),
                'Url': WeChatHandler.url_activity_detail(activity),
                'PicUrl': activity.pic_url,
            })

        if len(articles) == 0:
            return self.reply_text(self.get_message('book_empty'))

        return self.reply_news(articles)


class LookUpTicketHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        if self.user.student_id == '':  # not bind yet
            return self.reply_text(self.get_message('id_not_bind'))

        tickets = Ticket.objects.filter(
            status=Ticket.STATUS_VALID, student_id=self.user.student_id
        ).order_by('id')

        articles = []
        for ticket in tickets:
            activity = ticket.activity
            if activity.status == Activity.STATUS_PUBLISHED:  # deleted activity will be excluded
                articles.append({
                    'Title': self.get_message('ticket_title', activity=activity),
                    'Description': self.get_message('ticket_description', activity=activity),
                    'Url': self.url_ticket_detail(ticket),
                    'PicUrl': activity.pic_url,
                })

        if len(articles) == 0:
            return self.reply_text(self.get_message('ticket_empty'))

        return self.reply_news(articles)
