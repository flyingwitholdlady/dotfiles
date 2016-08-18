#!/usr/bin/env python
# -*- coding: utf-8 -*-



import requests
from requests.auth import HTTPBasicAuth
import os
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
        os.exit(0)

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
#def get_issues(session):
#    bug_list=[]
#    issue_page = REDMINE_URL + '/issues'
#    payload = { 'c[]':[ 'project', 'tracker', 'parent', 'status', 'priority',
#                        'subject', 'assigned_to', 'start_date', 'due_date', 'done_ratio',
#                        'cf_3'],
#                'f[]':['status_id', 'tracker_id','assigned_to_id', ''],
#                'group_by':'',
#                'op[assigned_to_id]' :'=',
#                'op[status_id]' :'=',
#                'op[tracker_id]' :'!',
#                'set_filter':1,
#                'utf8':'E2%9C%93',
#                'v[assigned_to_id][]':'me',
#                'v[status_id][]':[34, 8, 23, 17, 31, 33],
#                'v[tracker_id][]':[5],
#            }
#    r = request_page(session, issue_page, payload)
#    if r == None:
#        os.exit(0)
#
#    soup = BeautifulSoup(r.content, 'html.parser')
#    list_tasks = soup.find_all('tbody')
#    for child in list_tasks[0].children:
#        if not isinstance(child, NavigableString):
#            result={}
#            bug_id_tag = child.find_all('td', 'id')
#            if bug_id_tag and bug_id_tag[0].a:
#                result['bugid'] = bug_id_tag[0].a.contents[0]
#                #logging.info(result['bugid'])
#
#            project_tag = child.find_all('td', 'project')
#            if project_tag and project_tag[0].a:
#                result['project'] = project_tag[0].a.contents[0]
#                #logging.info(result['project'])
#
#            attr_tag = child.find_all('td', 'tracker')
#            if attr_tag and attr_tag[0].contents:
#                result['attr'] = attr_tag[0].contents[0]
#                logging.info(result['attr'])
#
#            status_tag = child.find_all('td', 'status')
#            if status_tag and status_tag[0].contents:
#                result['status'] = status_tag[0].contents[0]
#                #logging.info(result['status'])
#
#            priority_tag = child.find_all('td', 'priority')
#            if priority_tag and priority_tag[0].contents:
#                result['priority'] = priority_tag[0].contents[0]
#                #logging.info(result['priority'])
#
#            title_tag = child.find_all('td', 'subject')
#            if title_tag and title_tag[0].a:
#                result['title'] = title_tag[0].a.contents[0]
#                #logging.info(result['title'])
#
#            owner_tag = child.find_all('td', 'assigned_to')
#            if owner_tag and owner_tag[0].a:
#                result['owner'] = owner_tag[0].a.contents[0]
#                #logging.info(result['owner'])
#
#            start_date = child.find_all('td', 'start_date')
#            if start_date and start_date[0].contents:
#                result['start'] = start_date[0].contents[0]
#                #logging.info(result['start'])
#
#            due_date = child.find_all('td', 'due_date')
#            if due_date and due_date[0].contents:
#                result['end'] = due_date[0].contents[0]
#                #logging.info(result['end'])
#
#            progress = child.find_all('td', 'done_ratio')
#            if progress and progress[0].table:
#                result['progress'] = progress[0].table['class'][1][len('progress-'):]
#                #logging.info(result['progress'])
#
#            severity = child.find_all('td', 'cf_3')
#            if severity and severity[0].contents:
#                result['severity'] = severity[0].contents[0]
#                #logging.info(result['severity'])
#
#            bug_list.append(result)
#
#    return bug_list


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
        os.exit(0)
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

def delay_test(session, token):
    issue_url = REDMINE_URL + '/issues/67464'
    post_data =  {
        'authenticity_token': token,
        '_method': 'put',
        'utf8':'E2%9C%93',
        'commit':'%cc%e1%bd%bb',
        'issue[due_date]':'2016-08-20',
        'issue[notes]':'delay',
    }
    r = session.post(issue_url, headers=header, data=post_data)
    if r.status_code != requests.codes.ok:
        logging.error('POST:>>'+issue_url+'<< error:' + str(r.status_code))
        logging.error(r.raise_for_status())
        return None
    else:
        logging.info('user: '+ user + ' login success')
    return s, token[0]



def get_issues(session, auth = None, filter_dict=None):
    json_addr = '/issues.json'
    if filter_dict:
        json_addr += '?'
    for key in filter_dict:
        json_addr += key
        if filter_dict[key]:
            json_addr += str(filter_dict[key][0])
            json_addr += ','.join(filter_dict[key][1:])
        json_addr += '&'

    json_addr = json_addr[:-1]
    logging.info(json_addr)
    r = request_page(session, REDMINE_URL + json_addr, header=header, auth=auth)
    if r is None:
        os.exit(0)

    logging.info(r.content)



def get_status_list(state):
    pass

def main():
    setup_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="Username", required=True)
    parser.add_argument("-p", "--password", help="Password", required=True)
    args = parser.parse_args()
    session , token = user_login(args.user, args.password)
    auth = auth=HTTPBasicAuth(args.user, args.password)
    issue_filter = {'assigned_to_id':['=','me'],
                'status_id':['=','8', '23', '17', '31', '33'],
                'tracker_id':['!=','5'],
                }
    get_issues(session, auth, issue_filter)
    #users = get_operation_list(session)
    #delay_test(session, token)




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

