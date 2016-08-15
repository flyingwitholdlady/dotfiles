#!/usr/bin/env python
# -*- coding: utf-8 -*-



import requests
import os
import re
import logging
from bs4 import BeautifulSoup
import time
import datetime

REDMINE_URL='http://redmine.china-liantong.com:8000'


#head = {
#    "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36",
#}


def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(filename)s - %(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def user_login(user, pwd):
    header = {
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36",
    }
    login_url = REDMINE_URL + '/login'
    s = requests.session();
    r = request_page(s, login_url, header)
    if r == None:
        os.exit(0)

    token = re.findall('<input name="authenticity_token" type="hidden" value="(.*?)" />', r.content, re.S)
    post_data =  {
        'authenticity_token': token[0],
        'back_url': REDMINE_URL,
        'utf8':'E2%9C%93',
        'login': 'Login+%C2%BB',
        'password' : pwd,
        'username' : user,
    }
    r = s.post(login_url, headers=header, data=post_data)
    if r.status_code != requests.codes.ok:
        logging.error('POST:>>'+login_url+'<< error:' + r.status_code)
        return None
    else:
        logging.info('user: '+ user + ' login success')
    return s


def request_page(session, url, header=None):
    if header == None:
        header = {
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36",
        }
    r = session.get(url, headers=header)
    if r.status_code != requests.codes.ok:
        logging.error('GET:>>'+ login_url +'<< error:' + r.status_code)
        return None;
    return r

def get_last_7_hours(session):
    result={}
    my_page = REDMINE_URL + '/my/page'
    r = request_page(session, my_page)
    if r == None:
        logging.error('GET:>>'+ my_page +'<< error:' + r.status_code)
        return
    soup = BeautifulSoup(r.content, "html.parser")
    lists_days = soup.find_all('table','list time-entries')
    for child in lists_days[0].tbody.children:
        if child.name != None and child['class'][0].decode('utf-8') == 'odd':
            key=''
            value=''
            for td in child.children:
                if td.name != None:
                    if td.strong != None:
                        key = td.strong.contents[0];
                        if key ==  u'今天':
                            key = datetime.datetime.now().strftime('%Y-%m-%d');
                    elif td.has_attr('class'):
                        value = td.em.span.contents[0];
                    result[key] = value

    return result;


def main():
    setup_logger()
    #parser = argparse.ArgumentParser()
    #parser.add_argument("-u", "--user", help="Username", required=True)
    #parser.add_argument("-u", "--password", help="Password", required=True)
    #args = parser.parse_args()
    session = user_login('lynnding', 'Wasd1234')

    hours = get_last_7_hours(session)
    for key in hours:
        if int(hours[key]) < 8:
            logging.error('less than 8 hours in {0}'.format(key))










if __name__ == '__main__':
    main()






