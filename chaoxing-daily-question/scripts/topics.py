#!/usr/bin/env python3
"""列专栏话题。用法: python3 topics.py <bbsid> [folder_uuid] [--filter 关键词]"""
import datetime
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from cxlib import iter_topics  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith('--')]
kw = ''
if '--filter' in sys.argv:
    kw = sys.argv[sys.argv.index('--filter') + 1]

bbsid = args[0]
folder = args[1] if len(args) > 1 else ''

rows = []
for x in iter_topics(bbsid, folder):
    title = (x.get('title') or '').strip()
    if kw and kw not in title:
        continue
    ct = x.get('create_time') or 0
    date = datetime.datetime.fromtimestamp(ct / 1000).strftime('%Y-%m-%d') if ct else '-'
    rows.append((ct, '%s\t%s\t%s' % (date, x['uuid'], title)))
for _, line in sorted(rows):
    print(line)