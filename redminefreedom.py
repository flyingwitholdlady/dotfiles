#!/usr/bin/env python
# -*- coding: utf-8 -*-



import requests
import os
import re
import logging
from bs4 import BeautifulSoup, NavigableString
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
    login_url = REDMINE_URL + '/login'
    s = requests.session();
    r = request_page(s, login_url)
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
    header = {
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36",
    }
    r = s.post(login_url, headers=header, data=post_data)
    if r.status_code != requests.codes.ok:
        logging.error('POST:>>'+login_url+'<< error:' + str(r.status_code))
        return None
    else:
        logging.info('user: '+ user + ' login success')
    return s


def request_page(session, url, payload={}):
    header = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36",
    }
    r = session.get(url, params=payload, headers=header)
    if r.status_code != requests.codes.ok:
        logging.error('GET:>>'+ url +'<< error:' + str(r.status_code))
        logging.info(r.raise_for_status())
        return None;
    return r

def get_last_7_hours(session):
    result={}
    my_page = REDMINE_URL + '/my/page'
    r = request_page(session, my_page)
    if r == None:
        logging.error('GET:>>'+ my_page +'<< error:' + str(r.status_code))
        return
    soup = BeautifulSoup(r.content, "html.parser")
    lists_days = soup.find_all('table','list time-entries')
    for child in lists_days[0].tbody.children:
        if child.name != None and child['class'][0].decode('utf-8') == 'odd':
            key = child.find_all('strong')[0].contents[0]
            value = child.find_all('span', 'hours hours-int')[0].contents[0]
            result[key] = value
    return result;


def get_issues(session):
    bug_list=[]
    issue_page = REDMINE_URL + '/issues'
    payload = { 'c[]':[ 'project', 'tracker', 'parent', 'status', 'priority',
                        'subject', 'assigned_to', 'start_date', 'due_date', 'done_ratio',
                        'cf_3'],
                'f[]':['status_id', 'tracker_id','assigned_to_id', ''],
                'group_by':'',
                'op[assigned_to_id]' :'=',
                'op[status_id]' :'=',
                'op[tracker_id]' :'!',
                'set_filter':1,
                'utf8':'E2%9C%93',
                'v[assigned_to_id][]':'me',
                'v[status_id][]':[34, 8, 23, 17, 31, 33],
                'v[tracker_id][]':[5],
            }
    r = request_page(session, issue_page, payload)
    if r == None:
        os.exit(0)

    soup = BeautifulSoup(r.content, 'html.parser')
    f = open('1.html', 'w')
    f.write(unicode.encode(soup.prettify(), 'utf-8'))
    f.close()
    list_tasks = soup.find_all('tbody')
    for child in list_tasks[0].children:
        if not isinstance(child, NavigableString):
            result={}
            bug_id_tag = child.find_all('td', 'id')
            if bug_id_tag and bug_id_tag[0].a:
                result['bugid'] = bug_id_tag[0].a.contents[0]
                logging.info(result['bugid'])

            project_tag = child.find_all('td', 'project')
            if project_tag and project_tag[0].a:
                result['project'] = project_tag[0].a.contents[0]
                logging.info(result['project'])

            attr_tag = child.find_all('td', 'tracker')
            if attr_tag and attr_tag[0].contents:
                result['attr'] = attr_tag[0].contents[0]
                logging.info(result['attr'])

            status_tag = child.find_all('td', 'status')
            if status_tag and status_tag[0].contents:
                result['status'] = status_tag[0].contents[0]
                logging.info(result['status'])

            priority_tag = child.find_all('td', 'priority')
            if priority_tag and priority_tag[0].contents:
                result['priority'] = priority_tag[0].contents[0]
                logging.info(result['priority'])

            title_tag = child.find_all('td', 'subject')
            if title_tag and title_tag[0].a:
                result['title'] = title_tag[0].a.contents[0]
                logging.info(result['title'])

            owner_tag = child.find_all('td', 'assigned_to')
            if owner_tag and owner_tag[0].a:
                result['owner'] = owner_tag[0].a.contents[0]
                logging.info(result['owner'])

            start_date = child.find_all('td', 'start_date')
            if start_date and start_date[0].contents:
                result['start'] = start_date[0].contents[0]
                logging.info(result['start'])

            due_date = child.find_all('td', 'due_date')
            if due_date and due_date[0].contents:
                result['end'] = due_date[0].contents[0]
                logging.info(result['end'])

            progress = child.find_all('td', 'done_ratio')
            if progress and progress[0].table:
                result['progress'] = progress[0].table['class'][1][len('progress-'):]
                logging.info(result['progress'])

            severity = child.find_all('td', 'cf_3')
            if severity and severity[0].contents:
                result['severity'] = severity[0].contents[0]
                logging.info(result['severity'])

            bug_list.append(result)

    return bug_list

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
            logging.error('work {0} hours in {1} less than 8 hours'.format(hours[key], key))

    bugs = get_issues(session)
    logging.info(bugs)




if __name__ == '__main__':
    main()






