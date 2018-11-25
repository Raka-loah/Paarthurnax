【施工中】适用于[QQbot](https://github.com/pandolia/qqbot)的Warframe世界状态插件
---
**依赖**
requests、requests-cache用于拉取官方API状态。
beautifulsoup4用于分析某网页内容。
> pip install requests
> 
> pip install requests-cache
>
> pip install beautifulsoup4

**使用方法：**
1. 把所有的.py和.json复制到QQbot的插件文件夹，例如用户文件夹的.qqbot-tmp\plugins
2. 修改wf.py里的通报群名称
3. 启动QQbot，通过命令qq plug wf加载，或写入QQbot的配置文件自动加载
4. GROFIT!

**进度：**
- [x] 关键词通报（警报、入侵、裂缝、突击）
- [x] 平原时间（希图斯、福尔图娜）
- [x] 平原赏金（希图斯、福尔图娜）
- [x] 机器人自定义回复
- [x] 实时状态通报（警报、希图斯夜晚）
- [x] Roll/魔力8号球
- [x] 模拟开紫卡