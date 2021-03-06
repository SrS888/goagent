#!/usr/bin/env python
# coding=utf-8
# Contributor:
#      Goagent Helloworld        <goagent.helloworld@gmail.com>
import webapp2
import logging
import urllib
import time
import random
import sys
import re
from google.appengine.api import mail
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.runtime import apiproxy_errors
def urlfetch_QQ_isExsit(url):
    try:
        deadline=10
        response = urlfetch.fetch(url, method=urlfetch.GET,payload=None, headers={'Cache-Control': 'no-store'}, allow_truncated=False,follow_redirects=False, deadline=10)
        logging.info('status_code==%s url==%s', response.status_code, url)
    except apiproxy_errors.OverQuotaError as e:
        logging.error('OverQuotaError(deadline=%s, url=%r)', deadline, url)
        time.sleep(5)
    except urlfetch.DeadlineExceededError as e:
        logging.error('DeadlineExceededError(deadline=%s, url=%r)', deadline, url)
        time.sleep(1)
    except urlfetch.DownloadError as e:
        logging.error('DownloadError(deadline=%s, url=%r)', deadline, url)
    except urlfetch.ResponseTooLargeError as e:
        logging.error('ResponseTooLargeError(deadline=%s, url=%r) response(%r)', deadline, url, response)
    except Exception as e:
        logging.error('%s(deadline=%s, url=%r)',str(e), deadline, url)
    else:
        if response.status_code == 200:
            if 'goagent.html' in url:
                logging.info('fetch goagent.html success')
                return response.content
            if 'README.md' in url:
                logging.info('fetch github.com readme.md success')
                return response.content
            response = response.content.split('|')
            try:
                int(response[0])
            except ValueError:
                logging.warning('fetch %s,response result is invalid QQ No.',url)
                return None
            else:
                return response

    return None


def gae_sendmail(toadress):
    message = mail.EmailMessage(sender='GoAgent<shaozheng.wu@gmail.com>',
                            subject=unicode('使用GoAgent看YouTube视频,上BBC学英语','utf8'))

    message.bcc = toadress
    message.body = ''

    shareGoagentPage = urlfetch_QQ_isExsit('http://crater.herokuapp.com/uploads/goagent.html')
    if  shareGoagentPage:
        message.html = shareGoagentPage
    else:
        goagentPage = re.findall(r'"http.+goagent.html"', urlfetch_QQ_isExsit('https://github.com/325862401/spread_goagent/blob/appfog/README.md'))[0][1:-1]
        shareGoagentPage = urlfetch_QQ_isExsit(goagentPage)
        if  shareGoagentPage:
            message.html = shareGoagentPage
        else:
            logging.info('fetch goagent.html return None,Please check goagent.html page server ')
            fd = open('goagent.html', 'rb')
            message.html = fd.read()
            fd.close()
    """
    message.attachments =  [('goagenthome.jpg',db.Blob(open("goagenthome.jpg", "rb").read())),
                            ('IE_set.jpg',db.Blob(open("IE_set.jpg", "rb").read())),
                            ('ie_con_proxy.jpg',db.Blob(open("ie_con_proxy.jpg", "rb").read())),
                            ('proxy_set.jpg',db.Blob(open("proxy_set.jpg", "rb").read()))]
    """
    try:
        message.send()
    except Exception as e:
        logging.error('Mail sent fail by gae,please check code.')
        return False
    else:
        logging.info('Congratulations!Mail have been sent successfully by gae.')
        #self.response.out.write('Congratulations!Mail have been sent successfully by gae.')
        return True

class MainPage(webapp2.RequestHandler):
  def get(self,TEST=True):
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write('<html><head> \
                                <title>SpreadGoAent</title> \
                            </head><body>')

    QQSize = 100
    url_aws = "http://goagent.aws.af.cm/%d" %QQSize
    url_hp  = "http://scola.hp.af.cm/%d" %QQSize
    url_heroku = "http://crater.herokuapp.com/%d" %QQSize
    urlList = [url_aws,url_hp,url_heroku]
    random.shuffle(urlList)

    #url = "http://open.baidu.com/special/time/"

    response = urlfetch_QQ_isExsit(urlList[0])
    if response is None:
        response = urlfetch_QQ_isExsit(urlList[1])
        if response is None:
            response = urlfetch_QQ_isExsit(urlList[2])
    if not response:
        logging.warning('fetch QQ list,response result is None')
        mail.send_mail(sender='GoAgent<shaozheng.wu@gmail.com>',
                        to="Scola<325862401@qq.com>",
                        subject="goagent.aws.af.cm died",
                        body="""
        Dear Scola:
        http://goagent.aws.af.cm,crater.herokuapp.com and scola.hp.af.cm return None.Please check it.
        """)

        self.response.out.write('The response content is None<br>')
        self.response.out.write("""
      </body>
      </html>""")
        return False
    logging.info('urlfetch result is valid QQ num,happy')
    if TEST:
        response.pop()
        response.append('325862401')
        random.shuffle(response)
    self.response.out.write('The first is %s and the end is %s in the QQ list<br>' %(response[0],response[-1]))
    logging.debug('The first is %s and the end is %s in the QQ list' ,response[0],response[-1])

    numtoadr = lambda f: 'GoAgent<%s@qq.com>' %f
    addr = map(numtoadr, response)
    retval = gae_sendmail(addr)
    if retval:
        self.response.out.write('Congratulations!Mail have been sent successfully by gae.')
    else:
        self.response.out.write('Sorry!Mail have not sent by gae.')

    #response = urllib.urlopen('http://scola.hp.af.cm/').read()

    self.response.out.write("""
      </body>
      </html>""")
#if __name__ == '__main__':
logging.basicConfig(level=logging.INFO, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%b %d %H:%M:%S]')
app = webapp2.WSGIApplication([('/mail', MainPage)], debug=True)
