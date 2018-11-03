#!/usr/bin/env python
import logging
import pyquery
import argparse
import os
import re
import hashlib
from collections import Set
from requests import get
from requests import post
from bs4 import BeautifulSoup

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

'''
Plugin for crawler integration. Implements wg-gesucht
'''

PLUGIN_REGEX="http[s]://www.wg-gesucht.de\.*"

def run(html, first_run=False):

    soup = BeautifulSoup(html, 'html.parser')

    articles = soup.find_all('div', class_='row')
    m = soup.find_all('a', class_='detailansicht')
#    print(articles)
#    prices = soup.find_all

    for i in m:
        link =  i['href']
        if not re.match('[\w\-]+.[0-9]+.html', link):
            continue
        url = os.path.join('https://www.wg-gesucht.de/', link)

#        body = '<a href=\"%s\">url</a><b>info:</b><pre>%s</pre>' % (url, i.text)
        yield url 


    return

    for a in articles:
#        logging.log(logging.INFO, a.text)
        #price_size = [re.sub(r'[\s]+', ' ', t.text) for t in a.find_all('div', class_='detail-size-price-wrapper')]

        w = a.find('div', class_='detail-size-price-wrapper')
        b = a.find('h3', class_='headline headline-list-view printonly')
        d = a.find('p')
        e = a.find('div', class_="col-xs-7 col-sm-5")

        if not (d and b and w and e):
            continue

        res = [re.sub(r'[\s\n\r]+', ' ', t.text) for t in [b,w,d,e] if not t is None]

        if "Tage" in res[3] or "Tag" in res[3]:
            continue
        elif len(res) < 3:
            continue

        to_send = r'<b>%s</b>\n%s\n%s\n%s' % (res[0],res[1], res[2], res[3])
        if re.match('.*ab [0-9]+', to_send): 
            continue

        yield to_send


if __name__ == "__main__":

    test_filters=[
        "https://www.wg-gesucht.de/wohnungen-in-Stuttgart.124.2.1.0.html",
        "https://www.wg-gesucht.de/wg-zimmer-in-Stuttgart.124.0.1.0.html?csrf_token=&offer_filter=1&stadt_key=124&sort_column=&sort_order=&noDeact=&autocompinp=Stuttgart&country_code=&countrymanuel=&city_name=&city_id=124&category=0&rent_type=0&sMin=&rMax=&dFr=&hidden_dFrDe=&dTo=&hidden_dToDe=&radLat=&radLng=&radAdd=&radDis=0&wgFla=0&wgSea=0&wgSmo=0&wgAge=&wgMnF=0&wgMxT=0&sin=0&exc=0&hidden_rmMin=0&hidden_rmMax=0&pet=0&fur=0",
        "https://www.wg-gesucht.de/1-zimmer-wohnungen-in-Stuttgart.124.1.1.0.html?csrf_token=&offer_filter=1&stadt_key=124&sort_column=0&sort_order=&noDeact=&autocompinp=Stuttgart&country_code=&countrymanuel=&city_name=&city_id=124&category=1&rent_type=0&sMin=&rMax=&dFr=&hidden_dFrDe=&dTo=&hidden_dToDe=&radLat=&radLng=&radAdd=&radDis=0&hidden_wgFla=0&hidden_wgSea=0&hidden_wgSmo=0&hidden_wgAge=&hidden_wgMnF=0&hidden_wgMxT=0&sin=0&exc=0&hidden_rmMin=0&hidden_rmMax=0&pet=0&fur=0"
    ]

    parser = argparse.ArgumentParser(description='Test wggesucht plugin for scraper.')
    parser.add_argument('--test', '-t')


    args = parser.parse_args()

    prec_pages = args.test

    pages = [os.path.join(os.path.dirname(__file__), 'test_data', p) for p in  os.listdir(prec_pages)]
 #   logging.log(logging.INFO, str(pages))

    for index, page in enumerate(pages):
        with open(os.path.realpath(page), 'r') as html:
            for art in run(html.read(), "1234124", 'some filter', None ):
                logging.log(logging.INFO, '')

