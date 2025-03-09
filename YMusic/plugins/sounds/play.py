from YMusic import app
from YMusic.core import userbot
from YMusic.utils import ytDetails
from YMusic.utils.queue import QUEUE, add_to_queue
from YMusic.misc import SUDOERS

from pyrogram import filters

import asyncio
import random
import time
import http.cookiejar as cookielib
import os

import config

PLAY_COMMAND = ["شغل", "تشغيل"]

PREFIX = config.PREFIX

RPREFIX = config.RPREFIX

# مسار ملف الكوكيز
COOKIES_FILE = "cookies/cookies.txt"

# تحميل الكوكيز من الملف
def load_cookies():
    if os.path.exists(COOKIES_FILE):
        cookie_jar = cookielib.MozillaCookieJar(COOKIES_FILE)
        cookie_jar.load()
        return cookie_jar
    return None

# حفظ الكوكيز في الملف
def save_cookies(cookie_jar):
    if not os.path.exists("cookies"):
        os.makedirs("cookies")
    cookie_jar.save(COOKIES_FILE)

async def ytdl(format: str, link: str):
    cookie_jar = load_cookies()
    if cookie_jar:
        cookies = "; ".join([f"{cookie.name}={cookie.value}" for cookie in cookie_jar])
        command = f'yt-dlp --cookies "{cookies}" --geo-bypass -g -f "[height<=?720][width<=?1280]" {link}'
    else:
        command = f'yt-dlp --geo-bypass -g -f "[height<=?720][width<=?1280]" {link}'
    
    stdout, stderr = await bash(command)
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
async def _aPlay(_, message):
    start_time = time.time()
    chat_id = message.chat.id
    if (message.reply_to_message) is not None:
        if message.reply_to_message.audio or message.reply_to_message.voice:
            input_filename, m = await processReplyToMessage(message)
            if input_filename is None:
                await message.reply_text("-› رد على ملـف صـوتي أو شـي للبـحث .")
                return
            await m.edit(" سيَتمَ اެݪتشغِيݪ اެلانِ .")
            Status, Text = await userbot.playAudio(chat_id, input_filename)
            if Status == False:
                await m.edit(Text)
            else:
                if chat_id in QUEUE:
                    queue_num = add_to_queue(
                        chat_id, message.reply_to_message.audio.title[:19], message.reply_to_message.audio.duration, message.reply_to_message.audio.file_id, message.reply_to_message.link)
                    await m.edit(f"# {queue_num}\n{message.reply_to_message.audio.title[:19]}\nTera gaana queue me daal diya hu")
                    return
                finish_time = time.time()
                total_time_taken = str(int(finish_time - start_time)) + "s"
                await m.edit(f"-› تـم التشـغيل بنجـاح .\n\nS𝑜𝑛𝑔N𝑎𝑚𝑒:- [{message.reply_to_message.audio.title[:19]}]({message.reply_to_message.link})\nD𝑢𝑟𝑎𝑡𝑖𝑜𝑛:- {message.reply_to_message.audio.duration}\nT𝑖𝑚𝑒 𝑡𝑎𝑘𝑒𝑛 𝑡𝑜 𝑝𝑙𝑎𝑦:- {total_time_taken}", disable_web_page_preview=True)
    elif (len(message.command)) < 2:
        await message.reply_text("-› الامـر غلـط ترى .")
    else:
        m = await message.reply_text(" تَـم اެݪبَـحثَ .")
        query = message.text.split(" ", 1)[1]
        try:
            title, duration, link = await ytDetails.searchYt(query)
            if not link:
                await m.edit("-› لم يتم العثور على نتائج للاستعلام المقدم.")
                return
        except Exception as e:
            await message.reply_text(f"Error:- <code>{e}</code>")
            return
        await m.edit("-› جـاري التشغـيل .")
        format = "bestaudio"
        resp, songlink = await ytdl(format, link)
        if resp == 0:
            await m.edit(f"❌ حدث خطأ أثناء معالجة الرابط.\n\n» `{songlink}`")
            return
        else:
            if chat_id in QUEUE:
                queue_num = add_to_queue(
                    chat_id, title[:19], duration, songlink, link)
                await m.edit(f"# {queue_num}\n{title[:19]}\n**⪼**اެبشࢪ عيني ضفتها ݪݪانتضاࢪ .\n**⪼**طلب الحلو:- {message.from_user.mention}")
                return
            Status, Text = await userbot.playAudio(chat_id, songlink)
            if Status == False:
                await m.edit(Text)
            else:
                if duration is None:
                    duration = "Playing From LiveStream"
                add_to_queue(chat_id, title[:19], duration, songlink, link)
                finish_time = time.time()
                total_time_taken = str(int(finish_time - start_time)) + "s"
                await m.edit(f"-› تم التشـغيل بنجـاح .\n\nS𝑜𝑛𝑔N𝑎𝑚𝑒:- [{title[:19]}]({link})\nD𝑢𝑟𝑎𝑡𝑖𝑜𝑛:- {duration}\nT𝑖𝑚𝑒 𝑡𝑎𝑘𝑒𝑛 𝑡𝑜 𝑝𝑙𝑎𝑦:- {total_time_taken}\n𝑟𝑒𝑞𝑢𝑒𝑠𝑡𝑒𝑑 𝑏𝑦:- {message.from_user.mention}", disable_web_page_preview=True)
