#!/usr/bin/python
import telegram
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram.ext import DelayQueue
from telegram.ext import MessageQueue

from telegram.ext import messagequeue as mq

token = '536400210:AAF7-FzhpS308A4rN6-Wm9POHRPcEooMvlg'

class MQBot(telegram.bot.Bot):
    '''A subclass of Bot which delegates send method handling to MQ'''

    def __init__(self, is_queued_def=True, mqueue=None, *args, **kwargs):
        super(MQBot, self).__init__(token='536400210:AAF7-FzhpS308A4rN6-Wm9POHRPcEooMvlg', *args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        '''Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments'''
       # print(args)
        return super(MQBot, self).send_message(*args, **kwargs)


