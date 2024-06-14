from YMusic import app
from YMusic.core import userbot
from YMusic.utils import ytDetails
from YMusic.utils.queue import QUEUE, add_to_queue
from YMusic.misc import SUDOERS

from pyrogram import filters

import asyncio
import random
import time

import config

PLAY_COMMAND = ["شغل", "تشغيل"]

PREFIX = config.PREFIX

RPREFIX = config.RPREFIX


async def ytdl(format: str, link: str):
    stdout, stderr = await bash(f'yt-dlp --geo-bypass -g -f "[height<=?720][width<=?1280]" {link}')
    if stdout:
        return 1, stdout
    return 0, stderr


async def bash(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    err = stderr.decode().strip()
    out = stdout.decode().strip()
    return out, err


async def processReplyToMessage(message):
    msg = message.reply_to_message
    if msg.audio or msg.voice:
        m = await message.reply_text("Rukja...Tera Audio Download kar raha hu...")
        audio_original = await msg.download()
        input_filename = audio_original
        return input_filename, m
    else:
        return None


async def playWithLinks(link):
    if "&" in link:
        pass
    if "?" in link:
        pass

    return 0


@app.on_message((filters.command(PLAY_COMMAND, PREFIX) | filters.command(PLAY_COMMAND, RPREFIX)) & filters.group)
async def play(client, m: Message):
    replied = m.reply_to_message
    chat_id = m.chat.id
    m.chat.title
    if replied:
        if replied.audio or replied.voice:
            await m.delete()
            huehue = await replied.reply("**🥢 | يَتَمِ اެݪتـشغيݪ اެنتـظࢪ قݪـيلاެ**")
            dl = await replied.download()
            link = replied.link
            if replied.audio:
                if replied.audio.title:
                    songname = replied.audio.title[:35] + "..."
                else:
                    songname = replied.audio.file_name[:35] + "..."
            elif replied.voice:
                songname = "Voice Note"
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await huehue.delete()
                # await m.reply_to_message.delete()
                await m.reply_photo(
                    photo="https://l.top4top.io/p_2363dcjiw1.jpg",
                    caption=f"""
**العنوان : [{songname}]({link})
ايدي الدردشة : {chat_id}
طلب من : {m.from_user.mention}
قناة السورس : [ قناة السورس ](t.me/MUSICTTMATRIX)**
""",
                )
            else:
                await call_py.join_group_call(
                    chat_id,
                    AudioPiped(
                        dl,
                    ),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                await huehue.delete()
                # await m.reply_to_message.delete()
                await m.replyhttps_photo(
                    photo="https://l.top4top.io/p_2363dcjiw1.jpg",
                    caption=f"""
**تم تشغيل الاغنية 
**العنوان : [{songname}]({link})
ايدي الدردشة : {chat_id}
طلب من : {m.from_user.mention}
قناة السورس : [ قناة السورس ](t.me/MUSICTTMATRIX)**
""",
                )

    else:
        if len(m.command) < 2:
            await m.reply("يجب عليك الرد على الاغنيه او وضع اسمها مع الامر")
        else:
            await m.delete()
            huehue = await m.reply("🔎 جاري البحث الرجاء الانتظار ")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            if search == 0:
                await huehue.edit("- لم يتم العثور على شيء ")
            else:
                songname = search[0]
                url = search[1]
                duration = search[2]
                thumbnail = search[3]
                hm, ytlink = await ytdl(url)
                if hm == 0:
                    await huehue.edit(f"**- عذرا هناك خطأ ما** \n\n`{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                        await huehue.delete()
                        await m.reply_photo(
                            photo=f"{thumbnail}",
                            caption=f"""
**العنوان : [{songname}]({url})
المدة : {duration}
ايدي المحادثه : {chat_id}
طلب من : {m.from_user.mention}
قناة السورس : [ قناة السورس ](t.me/MUSICTTMATRIX)**
""",
                        )
                    else:
                        try:
                            await call_py.join_group_call(
                                chat_id,
                                AudioPiped(
                                    ytlink,
                                ),
                                stream_type=StreamType().pulse_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                            await huehue.delete()
                            # await m.reply_to_message.delete()
                            await m.reply_photo(
                                photo=f"{thumbnail}",
                                caption=f"""
**بدأ تشغيل الاغنية
**العنوان : [{songname}]({url})
المدة : {duration}
ايدي المحادثه : {chat_id}
طلب من : {m.from_user.mention}💻
قناة السورس : [ قناة السورس ](t.me/MUSICTTMATRIX)**
""",
                            )
                        except Exception as ep:
                            await huehue.edit(f"`{ep}`")

@app.on_message((filters.command(PLAY_COMMAND, PREFIX) | filters.command(PLAY_COMMAND, RPREFIX)) & SUDOERS)
async def _raPlay(_, message):
    start_time = time.time()
    if (message.reply_to_message) is not None:
        await message.reply_text("-› خـطأ .")
    elif (len(message.command)) < 3:
        await message.reply_text("-› الأمـر خـطأ .")
    else:
        m = await message.reply_text("-› التحميـل .")
        query = message.text.split(" ", 2)[2]
        msg_id = message.text.split(" ", 2)[1]
        title, duration, link = ytDetails.searchYt(query)
        await m.edit("-› يجـري التحميـل ...")
        format = "bestaudio"
        resp, songlink = await ytdl(format, link)
        if resp == 0:
            await m.edit(f"❌ yt-dl issues detected\n\n» `{songlink}`")
        else:
            Status, Text = await userbot.playAudio(msg_id, songlink)
            if Status == False:
                await m.edit(Text)
            else:
                if duration is None:
                    duration = "Playing From LiveStream"
                finish_time = time.time()
                total_time_taken = str(int(finish_time - start_time)) + "s"
                await m.edit(f"-› تم التشـغيل بنجـاح .\n\nS𝑜𝑛𝑔N𝑎𝑚𝑒:- [{title[:19]}]({link})\nD𝑢𝑟𝑎𝑡𝑖𝑜𝑛:- {duration}\nT𝑖𝑚𝑒 𝑡𝑎𝑘𝑒𝑛 𝑡𝑜 𝑝𝑙𝑎𝑦:- {total_time_taken}", disable_web_page_preview=True)
