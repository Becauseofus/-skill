#!/usr/bin/env python3
"""列小组专栏。用法: python3 folders.py <bbsid>"""
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from cxlib import topic_page  # noqa: E402

bbsid = sys.argv[1]
d = topic_page(bbsid) or {}
for f in d.get('folder_list') or []:
    print('%s\t%2s\t%s' % (f.get('folder_uuid'), f.get('count'), f.get('name')))