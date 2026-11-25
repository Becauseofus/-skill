#!/usr/bin/env python3
"""上传图片到学习通云盘，输出可直接用于发帖的 files_url。

用法: python3 upload.py <图片路径>
输出: <files_url>   （已拼好 rw/rh/_fileSize/_orientation=1）
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
from cxlib import UA, cookie  # noqa: E402
from PIL import Image  # noqa: E402

path = sys.argv[1]
CK = cookie()


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout


raw = sh('curl -s -H "Cookie: %s" -H "User-Agent: \'%s\'" --max-time 20 '
         '"https://noteyd.chaoxing.com/pc/files/getYunPanUploadUrl?from=group"' % (CK, UA))
url = json.loads(raw)['data']
res = sh("curl -s -X POST '%s' -H \"Cookie: %s\" -H \"User-Agent: '%s'\" -F 'file=@%s' --max-time 120"
         % (url, CK, UA, path.replace("'", "'\\''")))
d = json.loads(res)
if not d.get('result'):
    sys.exit('上传失败: ' + res[:300])
pv = d['data']['previewUrl']
w, h = Image.open(path).size
print(pv + ('&' if '?' in pv else '?') +
      'rw=%d&rh=%d&_fileSize=%d&_orientation=1' % (w, h, os.path.getsize(path)))