#!/usr/bin/env python
# -*- coding: utf-8 -*-



import requests
from requests.auth import HTTPBasicAuth
import os
import sys
import re
import json
import logging
import argparse
from bs4 import BeautifulSoup, NavigableString
import time
import datetime

REDMINE_URL='http://redmine.china-liantong.com:8000'

header = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36",
}

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
    r = s.post(login_url, headers=header, data=post_data)
    if r.status_code != requests.codes.ok:
        logging.error('POST:>>'+login_url+'<< error:' + str(r.status_code))
        return None, None
    else:
        logging.info('user: '+ user + ' login success')
    return s, token


def request_page(session, url, payload = None, header = None, auth = None):
    r = session.get(url, params=payload, auth=auth)
    if r.status_code != requests.codes.ok:
        logging.error('GET:>>'+ url +'<< error:' + str(r.status_code))
        logging.info(r.raise_for_status())
        return None;
    return r


#def get_last_7_hours(session):
#    result={}
#    my_page = REDMINE_URL + '/my/page'
#    r = request_page(session, my_page)
#    if r == None:
#        logging.error('GET:>>'+ my_page +'<< error:' + str(r.status_code))
#        return
#    soup = BeautifulSoup(r.content, "html.parser")
#    lists_days = soup.find_all('table','list time-entries')
#    for child in lists_days[0].tbody.children:
#        if child.name != None and child['class'][0].decode('utf-8') == 'odd':
#            key = child.find_all('strong')[0].contents[0]
#            ## for unicode today
#            if key == u'今天':
#                key = today()
#            value = child.find_all('span', 'hours hours-int')[0].contents[0]
#            result[key] = value
#    return result;
#
#

def today(ftime = None):
    now = datetime.datetime.now()
    fnow = now.strftime('%Y-%m-%d')
    if ftime is None:
        return fnow
    else:
        delta =  datetime.datetime.strptime(ftime, '%Y-%m-%d') - datetime.datetime.strptime(fnow, '%Y-%m-%d')
        return delta.days


def get_operation_list(session):
    ## hack it to get users
    issue_page = REDMINE_URL + '/issues'
    payload = { 'assigned_to_id': 'me', 'set_filter':1, 'priority':'desc,updated_on:desc'}
    r = request_page(session, issue_page, payload)
    if r == None:
        sys.exit()
    result = re.search('availableFilters = {.*?};', r.content)
    if result == None:
        logging.info('can\'t find availableFilters var')
    else:
        ## remove availableFilters and ';'
        json_data = result.group(0)[len('availableFilters = '):-1]
        dict_data = dict(json.loads(json_data))
        #logging.info(dict_data)
        logging.info(dict_data.keys())

        user_ids = dict_data['assigned_to_id']['values']

        tracker_ids = dict_data['tracker_id']['values']
        logging.info(tracker_ids)

        status_ids = dict_data['status_id']['values']
        logging.info(status_ids)

        priority_ids = dict_data['priority_id']['values']
        logging.info(priority_ids )

        #parent_issue_ids = dict_data['parent_issue_id']['values']
        #logging.info(parent_issue_ids)
        #tracker_ids = dict_data['fixed_version_id']['values']
        #logging.info(user_ids)

        #return user_ids, tracker_ids

#def delay_test(session, token):
#    issue_url = REDMINE_URL + '/issues/67464'
#    post_data =  {
#        'authenticity_token': token,
#        '_method': 'put',
#        'utf8':'E2%9C%93',
#        'commit':'%cc%e1%bd%bb',
#        'issue[due_date]':'2016-08-20',
#        'issue[notes]':'delay',
#    }
#    r = session.post(issue_url, headers=header, data=post_data)
#    if r.status_code != requests.codes.ok:
#        logging.error('POST:>>'+issue_url+'<< error:' + str(r.status_code))
#        logging.error(r.raise_for_status())
#        return None
#    else:
#        logging.info('user: '+ user + ' login success')
#    return s, token[0]



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
    #json_addr='/issues.json?assigned_to_id=me&tracker_id=!5&status_id=8|31'
    r = request_page(session, REDMINE_URL + json_addr, header=header, auth=auth)
    logging.info(REDMINE_URL + json_addr)
    if r is None:
        sys.exit()
    return dict(json.loads(r.content))



def show_issues_state(issues = []):
    for  issue in issues:
        out=''
        if 'id' in issue.keys():
            out += str(issue['id']).center(7)
            out += '||'
        if 'project' in issue.keys():
            out += issue['project']['name'].ljust(30)
            out += '||'
        if 'tracker' in issue.keys():
            out += issue['tracker']['name'].center(10)
            out += '||'
        if issue['status']:
            out += issue['status']['name'].center(20)
            out += '||'
        if issue['priority']:
            out += issue['priority']['name'].center(10)
            out += '||'
        if issue['subject']:
            out += issue['subject'].center(40)
            out += '||'
        if issue['start_date']:
            out += issue['start_date']
            out += '||'
        if 'due_date' in issue.keys():
            out += issue['due_date']
            out += '||'
        if issue['done_ratio']:
            out += (str(issue['done_ratio']) + '%')
            out += '||'
        logging.info(out)

def main():
    setup_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="Username", required=True)
    parser.add_argument("-p", "--password", help="Password", required=True)
    parser.add_argument("-d", "--delay", help="Delay", required=False, default='auto')
    args = parser.parse_args()
    session , token = user_login(args.user, args.password)
    auth = auth=HTTPBasicAuth(args.user, args.password)
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

    end_day = ''
    if args.delay == 'auto':
        end_day = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        ## delay tomorrow
    else:
        try:
            time.strptime(str(args.delay), "%Y-%m-%d")
            end_day = args.delay
        except:
            logging.error('{0} is not a valid date'.format(args.delay))
            return sys.exit()

    logging.info('delay to {0}'.format(end_day))

    show_issues_state(issues)
    for issue in issues:
        if issue.has_key('done_ratio') and int(issue['done_ratio']) == 100:
            logging.info('{0}  progress is 100, ignore'.format(issue['id']))
            continue
        if not issue.has_key('due_date'):
            logging.info('{0} have no end time, ignore'.format(issue['id']))
            continue
        delta = today(issue['due_date'])
        if delta <= 0:
            ##TODO
            logging.info('issue {0} is end at {1}, we need to delay'.format(issue['id'], issue['due_date']))
    #logging.info(issues)


    #hours = get_last_7_hours(session)
    #for key in hours:
    #    hour = int(hours[key])
    #    if  hour < 8:
    #        logging.error('work {0} hours in {1} less than 8 hours'.format(hour, key))
    #    elif hour > 14:
    #        ## TODO
    #        logging.error('work {0} hours in {1}, you have to send a email to your leader '.format(hour, key))

    #bugs = get_issues(session)

    #for bug in bugs:
    #    if bug.has_key('progress') and int(bug['progress']) == 100:
    #        logging.info('{0}  progress is 100, ignore'.format(bug['bugid']))
    #        continue
    #    if not bug.has_key('end'):
    #        logging.info('{0} have no end time, ignore'.format(bug['bugid']))
    #        continue
    #    delta = today(bug['end'])
    #    if delta <= 0:
    #        ##TODO
    #        logging.info('bug {0} is end at {1}, we need to delay'.format(bug['bugid'], bug['end']))


if __name__ == '__main__':
    main()

