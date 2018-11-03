#!/usr/bin/python
'''
Plugin for crawler integration. Implements autoscout
'''

def plugin_integration_test():
    print("Integration works!")


def crawl_autoscout(pq, flt, first_run=False):
    b_url = 'https://www.autoscout24.com/'
    for index, article in enumerate(reversed(pq('.cl-list-element'))):
        title = pq(article)('h2').text()
        site_s = pq(article)('a').attr('href')
        price = pq(article)('.cldt-price.sc-font-xl.sc-font-bold').text()
        #img_src = pq(article)('img')[1] #.attr('data-src')
        img_src = []
        for img in reversed(pq(article)('img')):
            img_src.append(pq(img).attr('data-src'))
        if not site_s:
            continue

        if not img_src:
            img_src = ''
        else:
            img_src = img_src[0]

        img_src = '<a href=\"%s\">img</a>' % img_src
        flt_link = '<a href=\"%s\">%s</a>' % (flt[1], 'filter')
        site = '<a href=\"https://www.autoscout24.com%s\">%s</a>' % (
            site_s, title)
        header = '%s: %s : %s\n' % (img_src, site, flt_link)
        body = '<b>Preis:</b><pre>%s</pre>\n' % (price)
        footer = "------------------------\n"

        text = "%s%s" % (header, body)

        h = hashlib.sha224(site_s.encode('utf-8')).hexdigest()


#        send_msg(chat_id=flt[0], text=text, parse_mode=telegram.ParseMode.HTML)
        with statelock:
            if first_run:
                state[flt[0]].append(h)
                continue
            elif index < 15:
                state[flt[0]].append(h)
                continue
            elif h in state[flt[0]]:
                continue
            else:
                send_msg(chat_id=flt[0], text=text,
                         parse_mode=telegram.ParseMode.HTML)
                state[flt[0]].append(h)

  #  print("autoscout flt found")
    pass

if __name__ == "__main__":
    pass
