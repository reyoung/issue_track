import datetime

import dateutil.parser
import pytz
import requests
import collections
import bottle
import json

sess = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=20)
sess.mount('http://', adapter)
sess.mount('https://', adapter)

local_tz = pytz.timezone('Asia/Shanghai')


def is_issue_today(issue):
    dt = dateutil.parser.parse(issue['created_at'])
    dt = dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return dt.date() == datetime.date.today()


@bottle.get('/')
def index():
    issues = []

    for i in xrange(10000):
        url = 'http://api.github.com/repos/PaddlePaddle/Paddle/issues?page={0}&state=all'.format(
            str(i))
        page = sess.get(url).json()
        issues.extend(page)
        if not is_issue_today(issues[-1]):
            break

    results = []
    name_dict = collections.defaultdict(int)
    for each_issue in issues:
        if 'pull_request' in each_issue:
            continue
        issue = dict()
        issue['name'] = each_issue['user']['login']
        issue['title'] = each_issue['title']
        name_dict[each_issue['user']['login']]+=1
        issue['label'] = []
        for lbl in each_issue['labels']:
            issue['label'].append(lbl['name'])
        if each_issue['milestone'] is None:
            issue['milestone'] = None
        else:
            issue['milestone'] = each_issue['milestone']['title']
        results.append(issue)



    result = {
        'rank': name_dict,
        'details': results
    }
    bottle.response.content_type = 'application/json'
    return json.dumps(result)

bottle.run(host="0.0.0.0", port=4000)