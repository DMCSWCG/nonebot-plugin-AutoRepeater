import nonebot
import re,os,time
from nonebot import on_message, on_command, on_notice
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.permission import SUPERUSER
from nonebot.params import CommandArg
from typing import Union
try:
    from nonebot.adapters.cqhttp import Bot, MessageSegment, GroupMessageEvent, Message, MessageEvent, GroupRecallNoticeEvent
    from nonebot.adapters.cqhttp.permission import GROUP_ADMIN, GROUP_OWNER
except ModuleNotFoundError as _:
    nonebot.logger.warning(
        "Nonebot version look like high then 2.0.0a16 to use high version adapters!"
    )
    try:
        from nonebot.adapters.onebot.v11 import Bot, MessageSegment, GroupMessageEvent, Message, MessageEvent, GroupRecallNoticeEvent
        from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
    except ModuleNotFoundError as _:
        raise ImportError("No support adapter find! Abort load!")
    
from nonebot.plugin import PluginMetadata
from .data_source import *

try:
    scheduler = nonebot.require("nonebot_plugin_apscheduler").scheduler
except Exception as e:
    nonebot.logger.error("Not find nonebot_plugin_apscheduler!Please install it!Abort Load!")
    raise ModuleNotFoundError

global_config = nonebot.get_driver().config
plugin_config = Config(**global_config.dict())
repeater = Repeater(plugin_config)

Repeat_Message_Config = on_command("自动+1设置",aliases={"自动复读","自动复读设置"}, permission=SUPERUSER|GROUP_ADMIN|GROUP_OWNER,priority=10)
@Repeat_Message_Config.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State,args: Message = CommandArg()):
    args = args.extract_plain_text()
    RepeatMessageConfig = ["关闭","开启"]
    #args = str(event.get_message()).strip()
    if not "group_id" in event.dict():
        await Repeat_Message_Config.finish("请在群中使用！")
    group_id = event.dict()["group_id"]
    Config_Data = await repeater.read_config()
    if not str(group_id) in Config_Data:
        Config_Data[f"{group_id}"] = False
    Set_State = 1 if Config_Data[f"{group_id}"] else 0
    now_mode = RepeatMessageConfig[Set_State]
    if not args or not args in RepeatMessageConfig:
        await Repeat_Message_Config.finish(f"没有输入需要设置的模式或输入有误！当前模式为{now_mode}!")
    new_index = RepeatMessageConfig.index(args)
    if new_index == Config_Data[f"{group_id}"]:
        await Repeat_Message_Config.finish(f"当前模式已经为{now_mode}")
    Config_Data[f"{group_id}"] = True if new_index==1 else False
    await repeater.write_config(Config_Data)
    await Repeat_Message_Config.finish(f"设置成功！设置自动复读功能为：{RepeatMessageConfig[new_index]}")

message_list = {}
repeat_after_message = []
sender_message_detail = {}

Repeat_Message = on_message(block=False,priority=99)
@Repeat_Message.handle()
async def _(bot:Bot,event:GroupMessageEvent,state:T_State):
    global message_list,repeat_after_message,sender_message_detail
    repeater_flag = False
    if not "group_id" in event.dict():
        return
    group_id = int(event.dict()["group_id"])
    if not await repeater.check_group_is_used(group_id):
        await Repeat_Message.finish()
    message_text = str(event.get_message())
    if repeat_after_message:
        for msg in repeat_after_message:
            if msg["group_id"] == group_id:
                match_ratio = SequenceMatcher(None, str(message_text),str(msg["msg"])).quick_ratio()
                if match_ratio >= 0.93:
                    return
    
    if not f"{group_id}" in message_list:
        message_list[f"{group_id}"]=[]
    
    for msg in event.get_message():
        if msg.type not in ["text","image","face"]:
            nonebot.logger.info("Other Type Message Ignore!")
            return
    if len(message_list[f"{group_id}"])<1:
        message_list[f"{group_id}"].append(message_text)
    else:
        message_list[f"{group_id}"].append(message_text)
        match_ratio = SequenceMatcher(None, str(message_list[f"{group_id}"][0]),str(message_list[f"{group_id}"][1])).quick_ratio()
        repeater_msg:Message = Message(message_list[f"{group_id}"][1])
        if match_ratio >= 0.90:
            repeat_after_message.append({"group_id":group_id,"msg":repeater_msg,"time":time.time()})
            repeater_flag = True
            message_list[f"{group_id}"]=[]
        else:
            message_list[f"{group_id}"] = []
            message_list[f"{group_id}"].append(Message(event.get_message()))
    
    if repeater_flag:
        repeater_message = None
        for msg in Message(repeater_msg):
            if repeater_message is None:
                if msg.type == "image":
                    repeater_message = MessageSegment.image(msg.data["url"])
                if msg.type == "face":
                    repeater_message = MessageSegment.face(msg.data["id"])
                if msg.type == "text":
                    repeater_message = MessageSegment.text(Message(msg).extract_plain_text())
            elif repeater_message is not None:
                if msg.type == "image":
                    repeater_message += MessageSegment.image(msg.data["url"])
                if msg.type == "face":
                    repeater_message += MessageSegment.face(msg.data["id"])
                if msg.type == "text":
                    repeater_message += MessageSegment.text(Message(msg).extract_plain_text())
        if repeater_message is None:
            return
        try:
            msg_id = await Repeat_Message.send(repeater_message)
        except Exception as e:
            nonebot.logger.error("复读失败！"+str(e))
        if not event.message_id in sender_message_detail:
            sender_message_detail[event.message_id] = {"message_id":msg_id["message_id"],"time":time.time()}
    await Repeat_Message.finish()
    

Repeat_Message_Recall = on_notice(block=True)
@Repeat_Message_Recall.handle()
async def _(matcher: Matcher, bot: Bot, event: GroupRecallNoticeEvent, state: T_State):
    global sender_message_detail
    if event.message_id in sender_message_detail:
        if abs(sender_message_detail[event.message_id]["time"]-time.time())<(60+59):
            try:
                await bot.delete_msg(message_id=sender_message_detail[event.message_id]["message_id"])
            except Exception as e:
                nonebot.logger.error(f"复读自动跟随撤回失败||{e}")
        sender_message_detail.pop(event.message_id)
    await Repeat_Message_Recall.finish()


@scheduler.scheduled_job("interval", seconds=30, jitter=5,id="UpLoadVideoState")
async def _():
    global repeat_after_message,sender_message_detail
    for repeat_msg in repeat_after_message:
        if abs(int(time.time()-repeat_msg["time"]))>repeater.repeat_interval:
            repeat_after_message.remove(repeat_msg)
    temp = []
    for key,values in sender_message_detail.items():
        if abs(int(time.time()-values["time"]))>179:
            temp.append(key)
    for key in temp:
        sender_message_detail.pop(key)
    return
