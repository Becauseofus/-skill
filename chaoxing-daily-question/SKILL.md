---
name: chaoxing-daily-question
version: 1.0.0
description: 超星学习通「每日一题」自动化。用于：检查某门课每日一题话题里自己有没有回复（哪天做了、哪天漏了）、批量补发手写答案图片、列出每日一题题库话题。触发词：学习通、超星、每日一题、班级空间、话题回复、补交、补发答案、课程讨论区。
---

# 学习通 每日一题

处理超星学习通的「每日一题」：查提交情况、补发答案图。

## 关键事实

- 「每日一题」= 班级**小组话题**，不是作业。作业接口（`/mooc2/work/list`）里查不到。
- 话题挂在小组下（`bbsid`），通常放在「每日一题」专栏里（`folder_uuid`），标题形如「每日一题（第N天）」。
- 判断"写没写" = 翻话题回复找自己的 `creater_name`。
- 网页版没有「班级空间」入口，但 `groupweb.chaoxing.com` 的 PC 页面能读能写。

## 前置：登录

1. `browser_use` 打开 `https://i.chaoxing.com`，让用户在浏览器里登录（手机号+验证码会弹**图形点选验证码**，要人工点；密码登录一般不弹）。
2. 登录成功（跳转 `mooc2-ans.chaoxing.com`）后取 Cookie：
   - `browser_use get_cookies` → 拿到 `env_cookies_*.sh`
   - 再打开任意 `groupweb.chaoxing.com` 页面，**再取一次** Cookie（写操作需要 `JSESSIONID.GroupTopic_WEB`）
3. 脚本用环境变量 `CX_COOKIE` 传 Cookie 头。

```bash
. /var/minis/offloads/env_cookies_xxx.sh && export CX_COOKIE="$BROWSER_COOKIE_HEADER"
```

Cookie 约几周过期，过期表现为接口 302 跳登录或返回空 `datas`。

## 流程

### 1. 找小组和专栏

```bash
python3 scripts/courses.py            # 列课程，拿 courseid/clazzid
python3 scripts/folders.py <bbsid>    # 列专栏，找名叫「每日一题」的 folder_uuid
```

不知道 bbsid 时：在 App 里打开一条每日一题 → 分享 → 复制链接，链接形如
`https://sharewh2.xuexi365.com/share/<uuid>?c=<bbsid>&t=2`，`c` 就是 bbsid。

### 2. 列话题

```bash
python3 scripts/topics.py <bbsid> <folder_uuid>
# 输出：日期<TAB>uuid<TAB>标题
```

### 3. 查提交情况

```bash
python3 scripts/check.py <bbsid> <folder_uuid> --name 张三
# 逐天扫描，输出 OK/NO；--stop-after 7 表示连续7天未写就停
```

首次扫描很慢（每天话题有数千条回复，20 条/页）。`--workers 4` 并行可提速，
但并发过高会触发限流（表现为某天扫描 0 条），失败就降到 2。

### 4. 补发答案图

上传（curl 可用，签名 URL 不校验 Cookie）：

```bash
python3 scripts/upload.py "/path/答案.png"
# 输出一行 files_url，已拼好 rw/rh/_fileSize/_orientation
```

发帖**必须走浏览器**：curl 直接 POST `/pc/invitation/{uuid}/addReplys` 会 302 到登录页
（缺 groupweb 会话）。在已登录的 groupweb 页面里执行 `execute_js`：

```js
const body=new URLSearchParams({replyId:'-1',uuid:crypto.randomUUID(),
  topic_content:'',files_url:'<上一步的 files_url>',files_attr:'',anonymous:''});
const r=await fetch('/pc/invitation/<topicUuid>/addReplys',
  {method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
   body:body.toString(),credentials:'include'});
return await r.text();   // {"msg":"回复发表成功",...}
```

- 一次 JS 调用发 3–4 条，每条间隔 8–9 秒；批量循环会返回「操作过于频繁」。
- 一次真实调用最多发 7 条也会被限流，宁慢勿快。
- 成功判据：返回 JSON 里 `msg` 含「回复发表成功」。
- 规则要求「只发图片」，所以 `topic_content` 留空。

## 坑位清单

| 现象 | 原因 |
|---|---|
| POST 返回 302 到 passport | 缺 `JSESSIONID.GroupTopic_WEB`，改用浏览器 fetch |
| `pageSize` 无效 | 服务端固定 20 条/页，只能用 `lastValue` 翻页 |
| 「操作过于频繁」 | 发帖限流，间隔 8–9 秒 |
| 「话题已结束，无法回复」 | 话题被关闭，无法补发（旧的专题常见） |
| 扫描到一半 `datas` 为 null | 请求过快，退避重试 + 降低并发 |
| 每日一题在 `activelist` 里找不到 | 它是话题不是活动；type 42 是「随堂练习」、2 是签到、45 是通知 |

## 参考

接口细节见 `references/api.md`。