#!/usr/bin/env python3
"""检查每日一题完成情况。

用法:
  python3 check.py <bbsid> <folder_uuid> --name 张三 [--stop-after 7] [--workers 4] [--days 3]
输出: 日期<TAB>标题<TAB>OK/NO<TAB>回复时间
"""
import argparse
import datetime
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from cxlib import iter_topics, reply_page  # noqa: E402


def scan(topic, name, days, max_pages):
    ct = topic.get('create_time') or 0
    deadline = ct + days * 86400 * 1000
    last, n, hit, last_t, ok = '', 0, None, ct, True
    for _ in range(max_pages):
        d = reply_page(topic['bbsid'] if 'bbsid' in topic else BBSID, topic['uuid'], last, 1)
        if not d or d.get('datas') is None:
            ok = False
            break
        rs = d['datas']
        if not rs:
            break
        n += len(rs)
        last_t = rs[-1].get('create_time') or last_t
        for x in rs:
            if x.get('creater_name') == name and hit is None:
                hit = x.get('create_time')
        nv = (d.get('poff') or {}).get('lastValue')
        if not nv:
            break
        last = nv
        if last_t > deadline:
            break
    return topic, hit, n, ok, last_t


p = argparse.ArgumentParser()
p.add_argument('bbsid')
p.add_argument('folder')
p.add_argument('--name', required=True)
p.add_argument('--stop-after', type=int, default=0)
p.add_argument('--workers', type=int, default=4)
p.add_argument('--days', type=int, default=3)
p.add_argument('--max-pages', type=int, default=200)
a = p.parse_args()

BBSID = a.bbsid
topics = [x for x in iter_topics(a.bbsid, a.folder) if (x.get('title') or '').strip()]
topics.sort(key=lambda x: x.get('create_time') or 0)
print('# 话题 %d 个' % len(topics), file=sys.stderr)

streak = 0
i = 0
while i < len(topics):
    batch = topics[i:i + a.workers]
    with ThreadPoolExecutor(max_workers=len(batch)) as ex:
        for topic, hit, n, ok, last_t in ex.map(lambda t: scan(t, a.name, a.days, a.max_pages), batch):
            ct = topic.get('create_time') or 0
            date = datetime.datetime.fromtimestamp(ct / 1000).strftime('%Y-%m-%d')
            if hit:
                hm = datetime.datetime.fromtimestamp(hit / 1000).strftime('%m-%d %H:%M')
                print('%s\t%s\tOK\t%s' % (date, topic['title'].strip()[:20], hm))
                streak = 0
            else:
                flag = 'NO' if ok else 'NO?'
                print('%s\t%s\t%s\t扫描%d条' % (date, topic['title'].strip()[:20], flag, n))
                streak += 1
            sys.stdout.flush()
            if a.stop_after and streak >= a.stop_after:
                print('# 连续 %d 天未写，停止' % streak, file=sys.stderr)
                sys.exit(0)
    i += a.workers
    time.sleep(0.2)