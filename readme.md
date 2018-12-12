【施工中】Warframe世界状态本地webAPI
---
**依赖**

flask-restful用于快速开启本地RESTful API。

requests、requests-cache用于拉取官方API状态。

beautifulsoup4用于分析某网页内容。
> pip install flask-restful requests requests-cache beautifulsoup4

**使用方法**
1. 修改app.py底部的参数，并直接用 python app.py 启动。
2. 把聊天内容POST到localhost:port。
3. 若符合特定内容[（参考CQ-HTTP）](https://cqhttp.cc/docs/4.7/#/Post)，则返回通报字符串（JSON，内容在reply），状态200，若不符合，返回空字符串，状态204。
4. 使用你喜欢的机器人平台获取返回值，发送到你想发送的地方。（目前格式为CQ的）

**建议**

为了安全性和性能建议使用真正的WSGI而不是这个debug服务器。

当然懒得配置的话这样用也一样。

**进度：**
- [x] 关键词通报（警报、入侵、裂缝、突击）
- [x] 平原时间（希图斯、福尔图娜）
- [x] 平原赏金（希图斯、福尔图娜）
- [x] 机器人自定义回复
- [x] 实时状态通报（警报、希图斯夜晚）
- [x] Roll/魔力8号球
- [x] 模拟开紫卡
