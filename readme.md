# 适用于酷Q机器人的Warframe世界状态插件

[![](https://img.shields.io/github/issues/Raka-loah/qqbot-plugin-warframe.svg)](https://github.com/Raka-loah/qqbot-plugin-warframe/issues)
![](https://img.shields.io/github/stars/Raka-loah/qqbot-plugin-warframe.svg)
[![](https://img.shields.io/github/license/Raka-loah/qqbot-plugin-warframe.svg)](https://github.com/Raka-loah/qqbot-plugin-warframe/blob/master/LICENSE)

**前置条件**
------

酷Q机器人的[HTTP API插件](https://github.com/richardchien/coolq-http-api)。

**Python依赖**
------

> pip install -r requirements.txt

易得 `virtualenv` 虚拟环境更适合操作，过程略，请读者自行求解。

**使用方法**
------

1. 把代码Clone到本地；
2. 把 `config-sample.py` 复制一份，改名 `config.py`，修改里面的设置；
3. 命令行用 `python app.py` 启动。
4. 设置酷Q的HTTP API插件POST到 `127.0.0.1:8888` 。
5. 这就可以了。

**建议**
------

为了安全性和性能建议不要直接把Flask用于生产环境（也就是直接运行 `python app.py`）。当然懒得配置的话这样用也一样，你没打算搞个机器人产业出来吧。

**可用的其他版本：**

`app_twistd.py`：可用于Twisted web服务器的版本，需要自行配置Twisted。

`app_quart.py`：据说性能更为强大的基于Quart框架的版本，需要 `pip install quart` ，之后用 `hypercorn app_quart:app -b 127.0.0.1:8888 --access-log -` 启动。


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
