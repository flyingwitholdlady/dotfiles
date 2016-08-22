#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from requests.auth import HTTPBasicAuth
import sys
import re
import json
import logging
import argparse
import time
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

REDMINE_URL=''

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def user_login(user, pwd):
    login_url = REDMINE_URL + '/login'
    s = requests.session();
    r = request_page(s, login_url)
    if r == None:
        sys.exit()

    token = re.findall('<input name="authenticity_token" type="hidden" value="(.*?)" />', r.content, re.S)[0]
    post_data =  {
        'authenticity_token': token,
        'back_url': REDMINE_URL,
        'utf8':'E2%9C%93',
        'login': 'Login+%C2%BB',
        'password' : pwd,
        'username' : user,
    }
    r = s.post(login_url, data=post_data)
    if r.status_code != requests.codes.ok:
        logging.error('POST:>>'+login_url+'<< error:' + str(r.status_code))
        return None, None
    else:
        logging.info('user: '+ user + ' login success')
    return s, token


def request_page(session, url, payload = None, header = None, auth = None):
    try:
        r = session.get(url, params=payload, auth=auth)
    except requests.HTTPError:
        logging.error('GET:>>'+ url +'<< error:' + str(r.status_code))
        logging.info(r.raise_for_status())
        return None;
    return r



def get_issues(session, auth = None, filter_dict=None):
    json_addr = '/issues.json'
    if filter_dict:
        json_addr += '?'
    for key in filter_dict:
        json_addr += key
        if filter_dict[key]:
            json_addr += str(filter_dict[key][0])
            json_addr += '|'.join(filter_dict[key][1:])
        json_addr += '&'

    json_addr = json_addr[:-1]
    r = request_page(session, REDMINE_URL + json_addr, auth=auth)
    if r is None:
        sys.exit()
    return dict(json.loads(r.content))



def show_issues_state(issues = []):
    for  issue in issues:
        value = {}
        value['id'] = str(issue.get('id', '')).center(7)
        value['tracker'] = issue.get('tracker', {}).get('name', '').center(10)
        value['status'] = issue.get('status', {}).get('name', '').center(20)
        value['start_date'] = issue.get('start_date', '').center(20)
        value['due_date'] = issue.get('due_date', '').center(20)
        value['done_ratio'] = (str(issue.get('done_ratio', '0')) + '%').center(20)
        #'project' issue['project']['name']
        #'priority' issue['priority']['name']
        #'subject' issue['subject']
        logging.info('|'.join(value.values()))


def get_time_spend_array(session, auth, date):
    des_url = '{0}/time_entries.json'.format(REDMINE_URL)
    payload = {
        'user_id' : 'me',
        'spent_on' : date,
    }
    r = request_page(session, des_url, auth = auth, payload = payload)
    time_entries = dict(json.loads(r.content))
    if time_entries['total_count'] == 0:
        return None
    else:
        # logging.info(time_entries['time_entries'])
        return time_entries['time_entries']



def issue_delay(session, auth, id, date):
    des_url = '{0}/issues/{1}.json'.format(REDMINE_URL, id)
    payload = {'issue':{}}
    payload['issue']['due_date'] = date
    payload['issue']['notes'] = 'delayed'
    jsond = json.dumps(payload)
    header = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36",
        "Content-Type": "application/json"
    }
    try:
        r = session.put(des_url, headers=header, data=jsond, auth=auth)
        logging.info('{0} have delayed to {1}'.format(id, date))
    except requests.HTTPError, msg:
        logging.error('delay issue {0} failed {0}'.format(id, msg))


def main():
    setup_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="Username", required=True)
    parser.add_argument("-p", "--password", help="Password", required=True)
    parser.add_argument("-d", "--delay", help="Delay", required=False, default='auto')
    parser.add_argument("-url", "--url", help="Url", required=True)
    args = parser.parse_args()

    global REDMINE_URL
    REDMINE_URL = args.url

    session , token = user_login(args.user, args.password)
    auth = HTTPBasicAuth(args.user, args.password)
    end_date = datetime.date.today()
    if args.delay == 'auto':
        ## delay tomorrow
        end_date = (datetime.date.today() + datetime.timedelta(days=1))
    else:
        try:
            end_date = time.strptime(str(args.delay), "%Y-%m-%d")
        except:
            logging.error('{0} is not a valid date'.format(args.delay))
            sys.exit()

    logging.info('delay to {0}'.format(end_date.strftime("%Y-%m-%d")))
    issue_filter = {'assigned_to_id':['=','me'],
                'status_id':['=', '31', '8', '23', '17','33'],
                'tracker_id':['=!','5'],
                }
    issues_dict = get_issues(session, auth, issue_filter)
    issues=[]
    if 'issues' in issues_dict.keys():
        issues = issues_dict['issues'];
    else:
        logging.info('can\'t get redmine issue!')
        sys.exit()


    show_issues_state(issues)
    for issue in issues:
        if issue.has_key('done_ratio') and int(issue['done_ratio']) == 100:
            logging.info('{0}  progress is 100, ignore'.format(issue['id']))
            continue
        if not issue.has_key('due_date'):
            logging.info('{0} have no end time, ignore'.format(issue['id']))
            continue
        if datetime.datetime.strptime(issue['due_date'],'%Y-%m-%d').date() < end_date:
            issue_delay(session, auth, issue['id'], end_date.strftime('%Y-%m-%d'))

    email_notify = 1
    try:
        mail_server = smtplib.SMTP('mail.xxxxx.com', 587)
        # mail_server.set_debuglevel(1)
        my_email_address = '{0}@xxxxx.com'.format(args.user)
        mail_server.login(my_email_address, args.password)

        msg = MIMEMultipart()
        msg['From'] = my_email_address
        msg['To'] = my_email_address
        msg['Subject'] = 'Robot Redmine Message'

    except smtplib.SMTPException, msg:
        logging.error('login email error {0}'.format(msg))
        email_notify = 0

    y_m_d_today = datetime.date.today().strftime('%Y-%m-%d')
    spend_array = get_time_spend_array(session, auth, date=y_m_d_today)
    if spend_array == None:
        logging.info('work 0 hours, rest?')
    else:
        hours = 0
        email_content = ''
        for spend in spend_array:
            hours += spend['hours']
        if hours < 8 or hours > 16:
            if email_notify == 1:
                email_content += 'work {0} hours in {1} \n'.format(str(hours), y_m_d_today)
                email_content += 'modify pls'
                msg.attach(MIMEText(email_content))
                mail_server.sendmail(my_email_address, my_email_address, msg.as_string())
            else:
                logging.info('work {0} hours in {1}'.format(str(hours), y_m_d_today))
        else:
            logging.info('work {0} hours in {1}'.format(str(hours), y_m_d_today))



if __name__ == '__main__':
    main()

