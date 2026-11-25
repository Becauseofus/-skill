#!/usr/bin/env python3
"""列课程（courseid / clazzid / 课程名 / 教师）。用法: python3 courses.py"""
import re
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from cxlib import cookie, UA  # noqa: E402
import urllib.request  # noqa: E402

BODY = b'courseType=1&courseFolderId=0&baseEducation=0&superstarClass=0&isComm=false'
req = urllib.request.Request('https://mooc1-1.chaoxing.com/visit/courselistdata', data=BODY, headers={
    'Cookie': cookie(), 'User-Agent': UA, 'Referer': 'https://mooc2-ans.chaoxing.com/'})
html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')

parts = html.split('<li class="course clearfix"')[1:]
for chunk in parts:
    chunk = chunk.split('<li class="course clearfix"')[0]
    cid = re.search(r'courseId="(\d+)"', chunk)
    kid = re.search(r'clazzId="(\d+)"', chunk)
    name = re.search(r'<span class="course-name[^"]*"[^>]*title="([^"]*)"', chunk) \
        or re.search(r'course-name[^>]*>([^<]+)<', chunk)
    teacher = re.search(r'<p class="line2" title="([^"]*)"', chunk)
    if cid and kid:
        print('%s\t%s\t%s\t%s' % (cid.group(1), kid.group(1),
                                  (name.group(1) if name else '?').strip(),
                                  teacher.group(1) if teacher else ''))