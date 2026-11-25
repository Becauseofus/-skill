# 接口速查

所有请求带 `Cookie`（浏览器登录态）和 `Referer: https://groupweb.chaoxing.com/`。

## 课程

```
POST https://mooc1-1.chaoxing.com/visit/courselistdata
data: courseType=1&courseFolderId=0&baseEducation=0&superstarClass=0&isComm=false
```

HTML 里 `<li class="course clearfix" courseId="..." clazzId="...">`，课程名在 `title="..."`。

## 话题列表（含专栏）

```
GET https://groupweb.chaoxing.com/pc/topic/topiclist/{bbsid}/getTopicListBySort
    ?folder_uuid=&startDate=&endDate=&pageSize=20
    &offsetValue={poff.lastValue}&lastAuxValue=&order=0&authMappId=&maxW=200&isOpen=1
```

- 返回 `datas[]`（uuid/title/create_time/s_replycount）、`folder_list[]`、`poff.lastValue`
- `pageSize` 无效，固定 20 条；下一页传 `offsetValue=poff.lastValue`
- `folder_uuid` 留空 = 全部；专栏列表来自 `folder_list`

## 话题回复

```
GET https://groupweb.chaoxing.com/pc/invitation/getReplyList
    ?bbsid={bbsid}&uuid={topicUuid}&order={1|2}&lastValue={poff.lastValue}
```

- `order=1` 正序（最早在前），`order=2` 倒序
- 每条含 `creater_name`、`create_time`（毫秒）、`floor`、`img_data[]`
- 固定 20 条/页

备用（分享域，规则相同，20 条/页，易限流）：

```
GET https://sharewh2.xuexi365.com/share/topic/{bbsid}/{topicUuid}/replys.json
    ?maxW=780&maxW2=260&lastValue=&top=0&order=1
```

## 图片上传

```
GET https://noteyd.chaoxing.com/pc/files/getYunPanUploadUrl?from=group
→ data = 带签名的上传地址（不校验 Cookie）

POST <该地址>  multipart: file=@xxx.png
→ result.data.previewUrl = https://p.cldisk.com/star4/{objectId}/origin.png
```

发帖时 `files_url` 需追加 `?rw=宽&rh=高&_fileSize=字节&_orientation=1`。

## 发回复

```
POST https://groupweb.chaoxing.com/pc/invitation/{topicUuid}/addReplys
Content-Type: application/x-www-form-urlencoded
body: replyId=-1&uuid={随机UUID}&topic_content={encodeURIComponent(文本)}&files_url={多个用;分隔}&files_attr=&anonymous=
```

- **curl 直接调会 302 到 passport**（缺 `JSESSIONID.GroupTopic_WEB` 写会话）。在已登录的
  groupweb 页面里用 `fetch(..., {credentials:'include'})` 调用可成功。
- 成功：`{"msg":"回复发表成功","datas":{...}}`
- 限流：`{"msg":"操作过于频繁，请稍后再试"}`，间隔 8–9 秒可稳定发
- 关闭：`{"msg":"话题已结束，无法回复"}`

## 活动流（查签到/随堂练习/通知，不是每日一题）

```
GET https://mobilelearn.chaoxing.com/v2/apis/active/student/activelist
    ?fid={fid}&courseId={cid}&classId={clazzid}&showNotStartedActive=0
```

`activeType`: 2=签到、14=讨论、42=随堂练习、45=通知。