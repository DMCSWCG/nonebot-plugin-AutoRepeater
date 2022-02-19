import difflib
import re
import time
import nonebot
from nonebot.typing import T_State
try:
    from nonebot.adapters.cqhttp import Bot,GroupMessageEvent,MessageSegment,Message
except:
    raise ImportError("Nonebot2 Adapter Error!")

from nonebot.plugin import on_message

try:
    repeat_interval = nonebot.get_driver().config.repeat_interval
except:
    repeat_interval = 300

if repeat_interval is None:
    repeat_interval = 300

scheduler = nonebot.require("nonebot_plugin_apscheduler").scheduler

@scheduler.scheduled_job("interval", seconds=1, id="RepeatRefresh")
async def _():
    global repeat_after_message
    for repeat_msg in repeat_after_message:
        if abs(int(time.time()-repeat_msg["time"]))>repeat_interval:
            repeat_after_message.remove(repeat_msg)

message_list = {}
repeat_after_message = []
Repeat_Message = on_message(block=False,priority=100)
@Repeat_Message.handle()
async def _(bot:Bot,event:GroupMessageEvent,state:T_State):
    global message_list,repeat_after_message
    repeater_flag = False
    group_id = event.group_id
    message_text = str(event.get_message())
    if repeat_after_message:
        for msg in repeat_after_message:
            if msg["group_id"] == group_id:
                match_ratio = difflib.SequenceMatcher(None, str(message_text),str(msg["msg"])).quick_ratio()
                if match_ratio > 0.95:
                    return
    
    if not f"{group_id}" in message_list:
        message_list[f"{group_id}"]=[]
    
    if re.findall("(CQ:at|CQ:json|CQ:forward|CQ:music|CQ:reply|CQ:anonymous|CQ:location|CQ:video|CQ:node|CQ:share|CQ:xml|CQ:contact)",message_text):
        nonebot.logger.debug("Other Type Message Ignore!")
        return

    if len(message_list[f"{group_id}"])<1:
        message_list[f"{group_id}"].append(message_text)
    else:
        message_list[f"{group_id}"].append(message_text)
        match_ratio = difflib.SequenceMatcher(None, str(message_list[f"{group_id}"][0]),str(message_list[f"{group_id}"][1])).quick_ratio()
        repeater_msg:Message = Message(message_list[f"{group_id}"][1])
        if match_ratio > 0.95:
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
            nonebot.logger.debug("Other Type Message Ignore!")
            return
        try:
            await Repeat_Message.send(repeater_message)
        except Exception as e:
            nonebot.logger.error("复读失败||"+str(e))
    await Repeat_Message.finish()
