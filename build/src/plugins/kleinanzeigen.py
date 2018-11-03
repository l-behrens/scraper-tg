#!/usr/bin/python
import os
import re
import hashlib
import threading
from bs4 import BeautifulSoup
import logging
import time
'''
Plugin for crawler integration. Implements ebay-kleinanzeigen
'''

PLUGIN_REGEX="http[s]://www.ebay-kleinanzeigen.de\.*"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


statelock = threading.Lock()

def run(html, first_run=False):

    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all('article')

    if not articles:
        return

    for index, article in enumerate(articles):
        try:
            utime = article.find('div', class_='aditem-addon')
            uinfo = article.find('div', class_='aditem-details')
            utext = article.find('div', class_='aditem-main').find('p')
            uimage = article.find(class_='imagebox')['data-imgsrc']
        except Exception as e:
            print("error: %s" % e)
            pass
        else:
            print(utime)
            if utime is None or uinfo is None or utext is None:
                print("error")
                continue
            if not 'Heute' in utime.text:
                continue
            if first_run:
                continue
            info = re.sub('\s+', ' ', uinfo.text.strip()).strip()
            text = utext.text
            t = re.sub('\s+', ' ', utime.text).strip()

            if not uimage:
                print(str(uimage))
                body = '<b>Preis/Ort:</b><pre>%s</pre>\newline<b>Hochgeladen:</b><pre>%s</pre>\newline<b>Beschreibung:</b><pre>%s</pre>\newline' % (info, t, text)
            else:
                body = '<a href=\"%s\">img</a><b>Preis/Ort:</b><pre>%s</pre><b>Hochgeladen:</b><pre>%s</pre><b>Beschreibung:</b><pre>%s</pre>' % (uimage, info, t, text)
    
            yield body


if __name__ == "__main__":
    '''
    Test run func
    '''

    sample_data = os.path.join(os.path.dirname(__file__), 'test_data', 'kleinanzeigen')

    for f in os.listdir(sample_data):
        abs_f = os.path.join(sample_data, f)
        with open(abs_f, 'r') as test:
            for ret in run(test.read()):
                print(ret)
