
<p align="center">
  <a><img src="http://tva1.sinaimg.cn/large/006APoFYly1fzdi7y0v9wg306o06ot8t.gif"></a>
</p>
<div align="center">

  # AutoRepeater
  ✨ 基于[NoneBot2](https://github.com/nonebot/nonebot2)的插件，群聊自动复读机 ✨
  </br>
  ✨ Auto Repeater ✨
</div>

## 功能介绍

连续发送2条相同消息，机器人就会自动+1。包括普通消息，QQ表情，还有图片（表情包）。支持图片夹文字和表情夹文字的消息!


参考于[nonebot-plugin-repeater](https://github.com/ninthseason/nonebot-plugin-repeater)插件。

使用字符串相似度判断是否自动+1，Maybe有BUG。

支持复读跟随撤回功能，防止有人使用机器人复读功能爆破账号。

## 用法简介
依赖插件:

- 需要安装\[[nonebot_plugin_apscheduler](https://github.com/nonebot/plugin-apscheduler)\]插件

两个全局配置：

```python

repeat_interval = 300 # 单位秒 复读同一条消息的时间间隔 默认间隔5分钟

repeater_config_path = "./data/repeater_config/" # 多群状态设置文件存放路径

```
使用指令:

- 你机器人的指令前缀+"自动+1设置","自动复读","自动复读设置"&emsp;+&emsp;["开启"/"关闭"]&emsp;控制机器人在当前群是否进行复读，可由管理员、群主和Superuser控制。

***
## 等待实现
- 多条消息复读
- Recall功能开关
- 图片使用hash比较,提高准确性
***
<a href="https://github.com/Utmost-Happiness-Planet/uhpstatus/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-GPL%20v3.0-orange" alt="license">
  </a>
  
  <a href="https://github.com/nonebot/nonebot2">
    <img src="https://img.shields.io/badge/nonebot-v2-red" alt="nonebot">
  </a> 
  
  <a href="">
    <img src="https://img.shields.io/badge/release-v0.1.4-blueviolet" alt="release">
</a>
