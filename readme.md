适用于酷Q机器人的Warframe世界状态插件
---
**前置条件**
酷Q机器人的[HTTP API插件](https://github.com/richardchien/coolq-http-api)。

**Python依赖**

flask-restful用于快速开启本地RESTful API。

requests、requests-cache用于拉取官方API状态。

beautifulsoup4用于分析某网页内容。

apscheduler用于定时拉取。
> pip install flask-restful requests requests-cache beautifulsoup4 apscheduler

**使用方法**

1. 修改app.py底部的参数（主要是定时通报的群号），并直接用 python app.py 启动。
2. 设置酷Q的HTTP API插件POST到127.0.0.1:8888。
3. 这就可以了。

**建议**

为了安全性和性能建议使用真正的WSGI而不是这个debug服务器。（例如Twisted web，使用app_twistd.py即可）

当然懒得配置的话这样用也一样。

**开发**

如果其它平台的机器人也能用HTTP API，你可以适当修改app.py内的回复payload格式，从而实现其他平台使用。

**进度：**
- [x] 关键词通报（警报、入侵、裂缝、突击、奸商、每日特惠）
- [x] 平原时间（希图斯、福尔图娜）
- [x] 平原赏金（希图斯、福尔图娜）
- [x] 机器人自定义回复
- [x] 实时状态通报（新出现警报、希图斯夜晚）
- [x] Roll/魔力8号球
- [x] 模拟开紫卡
- [x] 需要你自行挖掘的隐藏功能
