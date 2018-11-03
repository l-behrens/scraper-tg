#!/usr/bin/python

from contextlib import contextmanager
from contextlib import closing
import hashlib
import sqlite3
import logging
import os
import datetime
import time
'''
database backend for scraper
'''

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def doquery(query, args=[]):
    with sqlite3.connect('scraper.db') as db:
        with closing(db.cursor()) as c:
            c.execute(query, tuple(args))
            return [row for row in c]

def init_db():
    doquery('create table if not exists filters (uid text, filter text, ftable text)')

def new_filter(uid, fltr):
#    doquery('drop table filters')
    doquery('create table if not exists filters (uid text, filter text, ftable text)')

    query='''select ftable from filters where uid=? and filter=?'''
    args=[uid, fltr]
    res = [r[0] for r in doquery(query, args)]
    if len(res) == 0:
        query='''Insert into filters(uid, filter, ftable) VALUES(?,?,?)'''
        fltr = str(fltr.strip())
        ftable = hashlib.sha224(fltr.encode('utf-8')).hexdigest()[:5]
        args=[uid, fltr, ftable]

        doquery(query, args)
        logging.log(logging.INFO, 'filter registered: \"%s\"' % fltr )
        return ftable
    else:
        logging.log(logging.WARNING, 'filter already registered: \"%s\"' % fltr )
        tname = '%s_%s_%s' % ('user', uid, res[0])
        query = 'create table if not exists %s (data text, time timestamp default current_timestamp not null)' % str(tname)
        doquery(query)
        return tname

def del_filter(uid, fltr):
    try:
        doquery('''Delete from filters where uid = ? and filter = ?''', [uid, fltr])
    except Exception as e:
        logging.log(logging.ERROR, e)
        return False
    else:
        logging.log(logging.INFO, "deleting filter \"%s\" succeeds" % str(fltr))
        return True

#def get_ftable_name(uid, fltr):
#    uid = str(uid)
#    fltr = str(fltr.strip())
#    query = '''select ftable from filters where uid=? and filter=?'''
#    args = [uid, fltr]
#
#    res = [r[0] for r in  doquery(query, args)]
#    if not res:
#        new_filter(uid, fltr)
#        raise Exception('filter is'
#    else:
#        return '%s_%s_%s' % ('user', uid, res[0])
def get_uids():
    query = '''select distinct uid from filters'''
    while True:
        try:
            res = [r[0] for r  in doquery(query)]
        except:
            logging.log(logging.INFO, 'initializing db ...')
            init_db()
            logging.log(logging.INFO, 'done!')
        else:
            return res


def get_filters(uid):
    query='''select filter from filters where uid=?'''
    return [flt[0] for flt in doquery(query, [uid])]

def new_metadata(uid, fltr, data):
#     doquery('drop table user_%s' % str(uid))
     tname = new_filter(uid, fltr)
     query = 'create table if not exists %s (data text, time timestamp default current_timestamp not null)' % str(tname)
     doquery(query)

     res = doquery('select time from %s' % str(tname))

#     print(len(res))

     logging.log(logging.INFO, 'table size is: %s' % len(res))
     #time.sleep(0.1)
     if len(res) > 100:
         res = {time.mktime(datetime.datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S").timetuple()): r[0] for r in res}
         query = 'delete from %s where time=?' % str(tname)
         query2 = 'select * from %s where time=?' % str(tname)
         for i in range(len(data)):
             args = [res[min(res.keys())]]
             dt=doquery(query2, args)
             doquery(query, args)
             logging.log(logging.INFO, 'deleting from %s: entry with timestamp %s\nmatches: %s\amount: %s' % (tname, args[0], str(dt), len(dt)))
         pass

     for d in data:
         if is_new(uid, fltr, d):
             query = 'insert into %s (data) VALUES(?)' % str(tname)
             doquery(query, [d])
             logging.log(logging.INFO, 'buffering: %s' %d)
         else:
             logging.log(logging.WARNING, 'already buffered: %s' % d)

#     res = doquery('select * from user_%s' % str(uid))

def is_new(uid, fltr, d):
    tname = new_filter(uid, fltr)
    query='select data from %s where data=?' % str(tname)
    res = doquery(query, [d])
#    logging.log(logging.INFO,"is this noew? %s" % str(res))
    if len(res) > 0:
        return False
    else:
        #new_metadata(uid, fltr, [d])
        return True

def _insert_filters_txt():
    query = '''drop table if exists filters'''
    doquery(query)

    ffile = os.path.join(os.path.dirname(os.path.relpath(__file__)), 'filters.txt')
    with open(ffile, 'r') as f:
        for line in f:
            uid, flt = line.split(' ')
            uid = uid.strip()
            flt = flt.strip()

            new_filter(uid, flt)


if __name__ == "__main__":
#    myuid = '536516448'
#    _insert_filters_txt()
#    query='''SELECT * FROM sqlite_master WHERE type='table';'''
#    logging.log(logging.INFO, str(doquery(query)))
#    get_uids()
#    _insert_filters_txt()


 #   query = 'create table if not exists %s (data text, time timestamp default current_timestamp not null)' % str('abcdefg') 
 #   doquery(query)

#    for i in range(0, 200):
#        new_metadata(myuid, 'https://www.ebay-kleinanzeigen.de/s-auto-rad-boot/cr-500/k0c210', [str(i)])
#    is_new(myuid, 'test1')
#    print(int(datetime.datetime.now().timestamp()))
    #print(get_filters(myuid))
    pass
