# 🐉Paarthurnax [NEXT]

符合[OneBot](https://github.com/howmanybots/onebot)标准的Warframe世界状态通报~~机器人~~机器龙**插件**，昵称“老帕”

[NEXT] 指威力增强进化版，目前正在缓慢开发中，目前已基本实现之前实现过的通报功能。**请移步v1分支获取之前的可用版本**

[![](https://img.shields.io/github/issues/Raka-loah/qqbot-plugin-warframe.svg)](https://github.com/Raka-loah/qqbot-plugin-warframe/issues)
![](https://img.shields.io/github/stars/Raka-loah/qqbot-plugin-warframe.svg)
[![](https://img.shields.io/github/license/Raka-loah/qqbot-plugin-warframe.svg)](https://github.com/Raka-loah/qqbot-plugin-warframe/blob/master/LICENSE)

**关于少量功能差异**
------

真正的老帕由于包含不适合在Github公开的内容以及少量私货，故此部分内容未进行开源。


**致完全的Python新手**
------

关于Python环境的安装与配置方法，请参阅Python官方文档：[点击此处](https://docs.python.org/zh-cn/3.8/using/windows.html)。

对于Windows环境安装时建议勾选 `Add Python to PATH` 项目，后期使用较为方便。

**前置条件**
------

符合[OneBot](https://github.com/howmanybots/onebot/blob/master/ecosystem.md)标准的任意bot平台。

**Python依赖**
------

> pip install -r requirements.txt

易得 `virtualenv` 虚拟环境更适合操作，过程略，请读者自行求解。

附注：由于 `requirements.txt` 固定了包版本，若长期未更新，可使用 `req_toptier.txt` 当中的pip命令升级所有依赖包。

**使用方法**
------

永远不要将服务器直接开放到公网（因为我真的懒得写鉴权），如果真的需要，请通过Apache/Nginx进行反代，且禁止外界对 `admin` 子路径的访问。

如果你的服务器没有图形界面，也不想把 `admin` 子路径反代出去，可以本地跑一个相同的老帕，用浏览器设置提交后把 `settings/settings.json` 覆盖到服务器然后重启老帕。

1. 把代码Clone到本地；
2. 把 `Paarthurnax/config-sample.py` 复制一份，改名 `config.py`，修改里面的基本设置；
3. 命令行用 `python app.py` 启动。
4. 设置bot平台通过HTTP POST到 `127.0.0.1:8888` 。
5. 这就可以了。
6. 启动后可以访问 `http://127.0.0.1:8888/admin` 对设置进行微调，保存后需重启机器人。

**本插件的插件安装方法**
------

没错，老帕[NEXT]版本将几乎所有功能剥离成统一的插件形式，这有助于今后对于本机器人插件的插件的开发。~~套娃什么的最有爱了~~

请不要随意安装不明来源的插件。

1. 插件统一保存在 `Paarthurnax/plugins` ，其中 `p_` 开头的为官方插件。~~你当然可以删除这些插件，但是人不能，至少不应该……~~
2. 将你下载到插件复制到这个文件夹后，**重启机器人**。
3. 理论上这时候插件就已经加载成功了。

**建议**
------

为了安全性和性能建议不要直接把Flask用于生产环境（也就是直接运行 `python app.py`）。当然懒得配置的话这样用也一样，你没打算搞个机器人产业出来吧。

如果你配置了C的编译环境，安装 `pip install python-Levenshtein` 可以稍微对模糊查询提速，不强求。

**可用的其他版本：**

`app_quart.py`：据说性能更为强大的基于Quart框架的版本，需要 `pip install quart` ，之后用 `hypercorn app_quart:app -b 127.0.0.1:8888 --access-log -` 启动。根据老帕之前的压力测试，大概还没到必须要用quart的地步。

**进度：**
------
- [X] 删除源代码冗余内容与功能（如Twisted支持）
- [X] 重构老帕架构，将实际业务与机器人本身剥离：消息推送→老帕听到消息（`Talking_Dragon.hear`）→`Preprocessors`→`Plugins`→`Postprocessors`→返回回复内容
- [X] 改写原Warframe通报与其他功能为独立插件
- [X] 建立Preprocessor和Postprocessor机制，方便二次开发
- [X] 所有processor和命令的优先级设定
- [X] 建立网页版设置项，因为做UI什么的都比不上做网页跨平台
- [ ] 撰写插件标准文档
- [ ] [NEXT]版本上线，并不兼容之前版本