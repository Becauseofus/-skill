"""学习通接口公共工具。Cookie 从环境变量 CX_COOKIE 读取。"""
import json
import os
import time
import urllib.parse
import urllib.request

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
GROUP = 'https://groupweb.chaoxing.com'


def cookie():
    c = os.environ.get('CX_COOKIE', '').strip()
    if not c:
        raise SystemExit('缺少环境变量 CX_COOKIE：先 . env_cookies_xxx.sh 再 export CX_COOKIE="$BROWSER_COOKIE_HEADER"')
    return c


def get_json(url, referer='https://groupweb.chaoxing.com/', retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                'Cookie': cookie(), 'User-Agent': UA, 'Referer': referer})
            raw = urllib.request.urlopen(req, timeout=25).read().decode('utf-8', 'ignore')
            return json.loads(raw)
        except Exception:
            if i == retries - 1:
                return None
            time.sleep(1 + i)


def topic_page(bbsid, folder_uuid='', offset=''):
    q = urllib.parse.urlencode({
        'folder_uuid': folder_uuid, 'startDate': '', 'endDate': '', 'pageSize': '20',
        'offsetValue': offset, 'lastAuxValue': '', 'order': '0',
        'authMappId': '', 'maxW': '200', 'isOpen': '1'})
    return get_json('%s/pc/topic/topiclist/%s/getTopicListBySort?%s' % (GROUP, bbsid, q))


def iter_topics(bbsid, folder_uuid='', limit=60):
    offset = ''
    seen = set()
    for _ in range(limit):
        d = topic_page(bbsid, folder_uuid, offset)
        if not d or not d.get('datas'):
            return
        for x in d['datas']:
            if x['uuid'] in seen:
                continue
            seen.add(x['uuid'])
            yield x
        nv = (d.get('poff') or {}).get('lastValue')
        if not nv or nv == offset:
            return
        offset = nv


def reply_page(bbsid, uuid, last='', order=1):
    q = ('bbsid=%s&uuid=%s&order=%s&lastValue=%s' % (bbsid, uuid, order, last))
    return get_json('%s/pc/invitation/getReplyList?%s' % (GROUP, q))