#!/usr/bin/env python
from pprint import pprint

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from requests import get
from concurrent.futures import ThreadPoolExecutor
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram.ext import DelayQueue
from telegram.ext import MessageQueue
from telegram.ext import messagequeue as mq

from tempfile import NamedTemporaryFile
from io import StringIO
import subprocess
from io import StringIO
import sys
import argparse
import unittest
import hashlib
import tempfile
import telegram
import datetime
import hashlib
import threading
import asyncio
import os
import quopri
import pyquery
import logging
import time
import re
import shelve
from collections import deque
from mqbot import MQBot

from plugins import kleinanzeigen
from plugins import wggesucht
from plugins import *

import dbclient as data


statelock = threading.Lock()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

f_backup = os.path.dirname(os.path.abspath(__file__))+"/filters.txt"
myid = str(92464433)

#updater = Updater(token='536400210:AAF7-FzhpS308A4rN6-Wm9POHRPcEooMvlg')
#updater = Updater(token='416079354:AAGUTah4JjuRaC207IzjbiC4cv1p7gGvlTA')

#token='416079354:AAGUTah4JjuRaC207IzjbiC4cv1p7gGvlTA'
token = '536400210:AAF7-FzhpS308A4rN6-Wm9POHRPcEooMvlg'

#data = os.path.dirname(os.path.realpath(__file__))+'/data/data.shelve'
#d = {}

#{uid: {filter: deque(maxlen=10)}}

helptxt = '''
    folgende Bot befehle koennen benutzt werden:

    1. Filter hinzufuegen:
        Befehl:    /add <filter> <prio>
        Beispiel1:  /add https://www.ebay-kleinanzeigen.de/s-seite:2/cagiva/k0
    2. Filter loeschen
        Befehl     /del <filter>
        Beispiel:  /del https://www.ebay-kleinanzeigen.de/s-seite:2/cagiva/k0
    3. Filter auflisten
        Befehl     /show

    '''


def send_msg(chat_id, text, parse_mode=telegram.ParseMode.MARKDOWN, disable_preview=False):
#    if not str(chat_id)==str(myid):
 #   chat_id = str(chat_id)
 #   text = str(text)
    updater.bot.send_message(chat_id=myid, text=text, parse_mode=parse_mode,
                             disable_web_page_preview=disable_preview, reply_markup=None)
#    updater.bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode,
#                             disable_web_page_preview=False, reply_markup=None)
#

def start(bot, update):
    uid = str(update.message.chat_id)
    send_msg(chat_id=str(
        uid), text="Yeah, ich bin Interrail Gambo und reise durch Europa Ohne Geld in meiner Tasche mach ich Picknick in Mitropa!")

def add(bot, update, args):
    uid = str(update.message.chat_id)
    url = args[0]
    if len(args) == 2:
        uid = str(args[1])
    if len(args) == 1:
        url = str(args[0])

        if url.startswith("https://m.ebay"):
            url = re.sub("https://m.ebay", "https://www.ebay", url)

        data.new_filter(uid, url)
        text="filter hinzugefuegt!"
    elif len(args) > 2:
        text=helptext

    send_msg(chat_id=uid, text=text)

def delete(bot, update, args):
    if not len(args) == 1:
        text = "Nur ein Filterargument erlaubt. Aber %s sind gegeben:  %s" % (
            len(args), args)
    else:
        uid = str(update.message.chat_id)
        url = str(args[0])

        data.del_filter(uid, url)
        text = "filter geloescht: %s" % url

    send_msg(chat_id=update.message.chat_id, text=text)

def show_me_everything():
    uids = data.get_uids()

    for uid in uids:
        fltrs=data.get_filters(str(uid))

        text = ''
        i = 0
        while fltrs:
            if len(fltrs) >= 10:
                text=' '.join(['<b>%s</b>: <a href=\"%s\">%s</a>\n' % (i*10+index, f, f) for index, f in enumerate(fltrs[:10])])
                fltrs=fltrs[10:]
                i+=1
            else:
                text=' '.join(['<b>%s</b>: <a href=\"%s\">%s</a>\n' % (i*10+index, f, f) for index, f in enumerate(fltrs)])
            if text:
                send_msg(chat_id=myid, text=str(text), parse_mode=telegram.ParseMode.HTML, disable_preview=True)
                time.sleep(1)

def show(bot, update):
    uid = str(update.message.chat_id)
    fltrs=data.get_filters(str(uid))

    if uid==myid:
        show_me_everything()
        return

    text = ''
    i = 0
    while fltrs:
        if len(fltrs) >= 10:
            text=' '.join(['<b>%s</b>: <a href=\"%s\">%s</a>\n' % (i*10+index, f, f) for index, f in enumerate(fltrs[:10])])
            fltrs=fltrs[5:]
            i+=1
        else:
            text=' '.join(['<b>%s</b>: <a href=\"%s\">%s</a>\n' % (i*10+index, f, f) for index, f in enumerate(fltrs)])
            send_msg(chat_id=uid, text=str(text), parse_mode=telegram.ParseMode.HTML, disable_preview=True)
            break
        if text:
            send_msg(chat_id=uid, text=str(text), parse_mode=telegram.ParseMode.HTML, disable_preview=True)
            time.sleep(1)

def unknown(bot, update):
    text = ('\n').join(["Abenteuer Aklohol!", helptxt])
    send_msg(chat_id=update.message.chat_id, text=text)


def help_me(bot, update):
    send_msg(chat_id=update.message.chat_id, text=helptxt)

def _req_url(url):
    try:
        payload = {}
        payload['url'] = url
        ret = get(**payload)
        if not ret.status_code == 200:
            raise Exception("api not accessable")
    except Exception as e:
        logging.log(logging.WARNING, "api access not possible: %s" % str(e))
    else:
        return ret.text

def crawl_filters(bot, job, first_run=False):

    for uid in data.get_uids():
        logging.log(logging.INFO, "###############################:")
        logging.log(logging.INFO, "crawling filters for uid %s: %s" % (uid, len(data.get_filters(uid))))

        for index, flt in  enumerate(data.get_filters(uid)):
            ret = _req_url(flt)
            logging.log(logging.INFO, "crawling filter %s" % flt)

            try:
                pq = pyquery.PyQuery(ret)
            except Exception as e:
#                send_msg(myid, "Calling %s failed: %s" % (flt[1], e))
                logging.log(logging.WARNING, "calling ebay failed: %s" % e)
                continue
            func = None
            if re.match(kleinanzeigen.PLUGIN_REGEX, flt):
                func = kleinanzeigen.run
            elif 'autoscout24' in flt:
                func = autoscout.run
            elif re.match(wggesucht.PLUGIN_REGEX, flt):
                func = wggesucht.run
            else:
                '''
                if filter type not valid, bail out
                '''
                logging.log(logging.INFO, 'run function is not valid: %s' % func)
                continue


            for to_send in func(ret):
                to_hash = to_send.encode('utf-8')
                h = hashlib.sha224(to_hash)
                h = h.digest()

                '''
                In case of mismatch, bail out
                '''
                print('is new?')
                #print(type(data.is_new(uid, flt, str(h))))
                ndata = data.is_new(uid, flt, str(h))
                if not ndata:
                    logging.log(logging.INFO, 'end of Updates: %s' % to_send)
                    break
                else:
                    data.new_metadata(str(uid), str(flt), [str(h)])
                    logging.log(logging.INFO, "sending: %s" % to_send)
#                logging.log(logging.INFO, "sending: %s" % to_send)
                    send_msg(myid, to_send, telegram.ParseMode.HTML)




def formatted_list(bot, update):

    uid = '536516448'
    output = StringIO()
    f = os.path.join('/tmp', uid, 'filters.txt')

    if not os.path.isdir(os.path.dirname(f)):
        os.mkdir(os.path.abspath(os.path.dirname(f)))

    cont = '\n'.join(['#{: <3} {}'.format(c, flt) for c, flt in enumerate(data.get_filters(uid))])
#    f = NamedTemporaryFile()

    print(cont)
    with open(f, "w") as p:
        p.write(cont)

#    with open(f.name) as p:
#    print(open(f.name).read())
    bot.send_document(chat_id=uid, document=open(f, 'r'))
#    f.name = 'filters.txt'
#    with open(output, 'rw') as out:
#        out.write('\n'.join(['#{: <3} {}'.format(c, flt) for c, flt in enumerate(data.get_filters(uid))]))


#    os.remove(output)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="crawl the internet")
    parser.add_argument("-t", help="unittesting", action="store_true")
    parser.add_argument("-r", help="normal mode", action="store_true")

    args =  parser.parse_args()
    print(args.t)
    if args.t:
        unittest.main()
        sys.exit(0)

    from telegram.utils.request import Request
    r = Request(con_pool_size=8)


    mqbot = MQBot(token, request=r)
    updater = telegram.ext.updater.Updater(bot=mqbot, workers=4)

    j_queue = updater.job_queue
    dispatcher = updater.dispatcher

#    j_queue.run_once(create_shelve, 0)
#    j_queue.run_once(restore, 5)
    j_queue.run_repeating(crawl_filters, interval=300, first=0)
#    j_queue.run_repeating(backup_sync, interval=300, first=5)

    start_handler = CommandHandler('start', start)
    show_handler = CommandHandler('show', show)
    add_handler = CommandHandler('add', add, pass_args=True)
    del_handler = CommandHandler('del', delete, pass_args=True)
    #shell_handler = CommandHandler('sh', shell, pass_args=True)
    help_handler = CommandHandler('help', help_me)
    #list_handler = CommandHandler('list', formatted_list)
    unknown_handler = MessageHandler(Filters.command, unknown)

    dispatcher.add_handler(start_handler)
#    dispatcher.add_handler(shell_handler)
    dispatcher.add_handler(show_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(add_handler)
    dispatcher.add_handler(del_handler)
#    dispatcher.add_handler(list_handler)
    dispatcher.add_handler(unknown_handler)

    try:
        updater.start_polling()
    except Exception as e:
        send_msg(myid, "telegram Error: %s" % e)
