# 适用于酷Q机器人的Warframe世界状态插件

[![](https://img.shields.io/github/issues/Raka-loah/qqbot-plugin-warframe.svg)](https://github.com/Raka-loah/qqbot-plugin-warframe/issues)
![](https://img.shields.io/github/stars/Raka-loah/qqbot-plugin-warframe.svg)
[![](https://img.shields.io/github/license/Raka-loah/qqbot-plugin-warframe.svg)](https://github.com/Raka-loah/qqbot-plugin-warframe/blob/master/LICENSE)

**注意：2019/02/27更新后，请自行通过sqlite编辑软件将 `qqbot.sqlite` 中 `messages` 表的 `id` 字段取消主键，或直接删除后重新运行。**

CQ客户端的消息id并不是唯一的，之前版本因主键约束会导致消息无法正常录入数据库，部分与历史消息相关的功能会不可用。

**前置条件**
------

酷Q机器人的[HTTP API插件](https://github.com/richardchien/coolq-http-api)。

**Python依赖**
------

`flask-restful`用于快速开启本地RESTful API；
`requests`、`requests-cache`用于拉取官方API状态；
`beautifulsoup4`用于分析某网页内容；
`apscheduler`用于定时拉取；
`fuzzywuzzy`用于模糊查询。
> pip install flask-restful requests requests-cache beautifulsoup4 apscheduler fuzzywuzzy[speedup]

**使用方法**
------

1. 把代码Clone到本地；
2. 把 `config-sample.py` 复制一份，改名 `config.py`，修改里面的设置；
3. 命令行用 `python app.py` 启动。
4. 设置酷Q的HTTP API插件POST到 `127.0.0.1:8888` 。
5. 这就可以了。

**建议**
------

为了安全性和性能建议使用真正的WSGI而不是这个debug服务器。（例如Twisted web，使用app_twistd.py即可）

当然懒得配置的话这样用也一样。

**开发**
------

如果其它平台的机器人也能用HTTP API，你可以适当修改 `app.py` 内的回复payload格式，从而实现其他平台使用。

**进度：**
------
- [x] 关键词通报（警报、入侵、裂缝、突击、奸商、日常、周常、小小黑、每日特惠等）
- [x] 平原时间（希图斯、福尔图娜）
- [x] 平原赏金（希图斯、福尔图娜）
- [x] 机器人自定义回复
- [x] 实时状态通报（新出现警报、希图斯夜晚、新出现小小黑）
- [x] Roll/魔力8号球
- [x] 模拟开紫卡
- [x] 需要你自行挖掘的隐藏功能
